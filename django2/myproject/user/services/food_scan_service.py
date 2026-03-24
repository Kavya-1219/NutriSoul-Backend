import json
import logging
import re

import google.generativeai as genai
import typing as t
from django.conf import settings
from django.db.models import Sum, F, FloatField
from django.utils import timezone

from ..models import UserProfile, FoodLog

logger = logging.getLogger(__name__)


class NutritionSchema(t.TypedDict):
    calories: float
    protein: float
    carbs: float
    fats: float
    fiber: float
    sugar: float
    saturatedFat: float
    vitaminA: float
    vitaminC: float
    vitaminD: float
    vitaminB12: float
    calcium: float
    iron: float
    magnesium: float
    potassium: float
    sodium: float
    zinc: float


class FoodItemSchema(t.TypedDict):
    name: str
    confidence: float
    estimated_per_100g: NutritionSchema
    healthier_alternative: str
    pro_tip: str


class FoodResponseSchema(t.TypedDict):
    items: list[FoodItemSchema]


class FoodScanService:
    # Set to True to verify frontend is working independently of Gemini API
    DEBUG_HARDCODE_IDLI = False

    BLACKLIST = {
        "textile", "wool", "toy", "fabric", "clothing", "pattern", "product",
        "person", "human", "furniture", "table", "bottle", "wrapper", "background",
        "plate", "dish", "bowl", "spoon", "fork", "knife", "utensil", "cutlery",
        "hand", "finger", "countertop", "floor", "wall", "window"
    }

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.model_name = "gemini-2.5-flash"

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                logger.exception("NUTRI-DYNAMIC: Gemini configure failed")

    def scan_food(self, image_file, additional_text="", user=None):
        logger.info("NUTRI-DYNAMIC: Food scan started")

        if self.DEBUG_HARDCODE_IDLI:
            logger.warning("NUTRI-DYNAMIC: DEBUG_HARDCODE_IDLI is ON")
            items = [
                self._normalized_result(
                    name="Idli",
                    calories=58,
                    protein=2.0,
                    carbs=12.0,
                    fats=0.2,
                    fiber=0.5,
                    confidence=0.99,
                    pro_tip="Debug hardcoded result.",
                    healthier_alternative="",
                    source="Debug"
                ),
                self._normalized_result(
                    name="Sambar",
                    calories=80,
                    protein=3.5,
                    carbs=12.0,
                    fats=2.5,
                    fiber=3.0,
                    confidence=0.99,
                    pro_tip="Debug hardcoded result.",
                    healthier_alternative="",
                    source="Debug"
                ),
            ]
            return self._personalize_results(items, user), "success"

        try:
            image_bytes = image_file.read()
            image_file.seek(0)
        except Exception:
            logger.exception("NUTRI-DYNAMIC: Failed reading image bytes")
            image_bytes = None

        ai_results, error_type = self._try_ai_detection(image_bytes, additional_text)
        if ai_results:
            return self._personalize_results(ai_results, user), "success"

        if error_type == "quota" or error_type == "all_models_failed":
            msg = "AI scan temporarily unavailable due to quota or system limits. Please try again later or log food manually."
        elif error_type == "forbidden":
            msg = "AI configuration error (API Key). Please contact support."
        elif error_type == "model_not_found":
            msg = "Selected AI models are currently unavailable. Please try again later."
        else:
            msg = "Could not identify food confidently from the image. Please confirm food name manually."

        logger.warning("NUTRI-DYNAMIC: AI result failed (%s), returning uncertain response", error_type)
        uncertain = [self._normalized_result(
            name="Uncertain result",
            calories=0,
            protein=0,
            carbs=0,
            fats=0,
            fiber=0,
            sugar=0,
            saturatedFat=0,
            vitaminA=0,
            vitaminC=0,
            vitaminD=0,
            vitaminB12=0,
            calcium=0,
            iron=0,
            magnesium=0,
            potassium=0,
            sodium=0,
            zinc=0,
            confidence=0.0,
            pro_tip=msg,
            healthier_alternative="Search and select the correct food item manually.",
            source="Uncertain"
        )]
        return uncertain, "Low-confidence"

    def _try_ai_detection(self, image_bytes, additional_text=""):
        if not self.api_key or not image_bytes:
            logger.warning("NUTRI-DYNAMIC: Missing API key or image bytes")
            return None, "missing_dependencies"

        prompt = self._build_prompt(additional_text)
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-1.5-flash-latest",
        ]

        for model_name in models_to_try:
            try:
                logger.info("NUTRI-DYNAMIC: Trying model %s", model_name)
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=FoodResponseSchema
                    )
                )

                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes}
                ])

                raw_text = getattr(response, "text", "") or ""
                if not raw_text:
                    logger.warning("NUTRI-DYNAMIC: Empty response from %s", model_name)
                    continue

                payload = json.loads(raw_text)
                items = payload.get("items", [])
                results = []

                for item in items:
                    mapped = self._map_ai_item(item)
                    if mapped:
                        results.append(mapped)

                results = self._dedupe_results(results)
                if results:
                    logger.info("NUTRI-DYNAMIC: AI detection succeeded with model %s", model_name)
                    return results, "success"

            except Exception as e:
                err_msg = str(e).lower()
                logger.warning("NUTRI-DYNAMIC: Model %s failed: %s", model_name, err_msg)
                
                if "429" in err_msg or "quota" in err_msg:
                    # Quota issue - try next model
                    continue
                elif "404" in err_msg or "not found" in err_msg:
                    # Model not supported/found - try next model
                    continue
                elif "403" in err_msg or "permission" in err_msg:
                    # API key or project issue - stop entirely
                    logger.error("NUTRI-DYNAMIC: Critical API key/permission error (403). Stopping fallback.")
                    return None, "forbidden"
                else:
                    # Other errors - try next model
                    continue

        return None, "all_models_failed"

    def _map_ai_item(self, item):
        if not isinstance(item, dict):
            return None

        name = (item.get("name") or "").strip()
        if not name:
            return None

        if name.lower() in self.BLACKLIST:
            return None

        confidence = self._safe_float(item.get("confidence"), 0.0)
        if confidence < 0.25:
            return None

        est = item.get("estimated_per_100g") or {}
        pro_tip = item.get("pro_tip", "") or ""

        if confidence < 0.60:
            pro_tip = f"Estimated AI result. Please confirm food name and serving size. {pro_tip}".strip()

        return self._normalized_result(
            name=name.title(),
            calories=self._safe_float(est.get("calories"), 0.0),
            protein=self._safe_float(est.get("protein"), 0.0),
            carbs=self._safe_float(est.get("carbs"), 0.0),
            fats=self._safe_float(est.get("fats"), 0.0),
            fiber=self._safe_float(est.get("fiber"), 0.0),
            sugar=self._safe_float(est.get("sugar"), 0.0),
            saturatedFat=self._safe_float(est.get("saturatedFat"), 0.0),
            vitaminA=self._safe_float(est.get("vitaminA"), 0.0),
            vitaminC=self._safe_float(est.get("vitaminC"), 0.0),
            vitaminD=self._safe_float(est.get("vitaminD"), 0.0),
            vitaminB12=self._safe_float(est.get("vitaminB12"), 0.0),
            calcium=self._safe_float(est.get("calcium"), 0.0),
            iron=self._safe_float(est.get("iron"), 0.0),
            magnesium=self._safe_float(est.get("magnesium"), 0.0),
            potassium=self._safe_float(est.get("potassium"), 0.0),
            sodium=self._safe_float(est.get("sodium"), 0.0),
            zinc=self._safe_float(est.get("zinc"), 0.0),
            confidence=confidence,
            pro_tip=pro_tip,
            healthier_alternative=item.get("healthier_alternative", "") or "",
            source="AI-Vision"
        )

    def _build_prompt(self, additional_text=""):
        prompt = """
You are a professional food vision and nutrition estimation assistant.
Analyze the uploaded food image and provide nutrition details.

Rules:
- Use the image as the main source of truth.
- Identify actual visible foods only.
- Ignore pates, bowls, spoons, and background.
- Estimate nutrition dynamically from the image.
""".strip()

        if additional_text:
            prompt += f"\nUser context: {additional_text.strip()}"

        return prompt

    def _dedupe_results(self, items):
        seen = set()
        out = []
        for item in items:
            key = (item.get("name") or "").strip().lower()
            if key and key not in seen:
                out.append(item)
                seen.add(key)
        return out

    def _normalized_result(
        self,
        name,
        calories,
        protein,
        carbs,
        fats,
        fiber=0,
        sugar=0,
        saturatedFat=0,
        vitaminA=0,
        vitaminC=0,
        vitaminD=0,
        vitaminB12=0,
        calcium=0,
        iron=0,
        magnesium=0,
        potassium=0,
        sodium=0,
        zinc=0,
        servingQuantity=100.0,
        servingUnit="g",
        confidence=0.0,
        healthier_alternative="",
        pro_tip="",
        source="Unknown"
    ):
        return {
            "name": str(name).strip(),
            "calories": round(float(calories), 1),
            "protein": round(float(protein), 1),
            "carbs": round(float(carbs), 1),
            "fats": round(float(fats), 1),
            "fiber": round(float(fiber), 1),
            "sugar": round(float(sugar), 1),
            "saturatedFat": round(float(saturatedFat), 1),
            "vitaminA": round(float(vitaminA), 1),
            "vitaminC": round(float(vitaminC), 1),
            "vitaminD": round(float(vitaminD), 1),
            "vitaminB12": round(float(vitaminB12), 1),
            "calcium": round(float(calcium), 1),
            "iron": round(float(iron), 1),
            "magnesium": round(float(magnesium), 1),
            "potassium": round(float(potassium), 1),
            "sodium": round(float(sodium), 1),
            "zinc": round(float(zinc), 1),
            "healthier_alternative": healthier_alternative or "",
            "pro_tip": pro_tip or "",
            "servingQuantity": round(float(servingQuantity), 1),
            "servingUnit": servingUnit or "g",
            "confidence": round(float(confidence), 2),
            "source": source,
        }

    def _safe_float(self, value, default=0.0):
        try:
            return float(value)
        except Exception:
            return default

    def _personalize_results(self, items, user):
        if not user or not getattr(user, "is_authenticated", False):
            return items

        profile = UserProfile.objects.filter(user=user).first()
        if not profile:
            return items

        today = timezone.localdate()
        consumed = FoodLog.objects.filter(
            user=user,
            timestamp__date=today
        ).aggregate(
            total=Sum(F("calories_per_unit") * F("quantity"), output_field=FloatField())
        )["total"] or 0.0

        target_calories = 2000.0
        try:
            calc_target = profile.calculate_calorie_goal()
            if calc_target and calc_target > 0:
                target_calories = float(calc_target)
            elif profile.target_calories:
                target_calories = float(profile.target_calories)
        except Exception:
            if profile.target_calories:
                target_calories = float(profile.target_calories)

        remaining = max(0.0, target_calories - consumed)

        allergies = self._normalize_list(profile.food_allergies) + self._normalize_list(profile.allergies)
        dislikes = self._normalize_list(profile.dislikes) + self._normalize_text_list(profile.food_dislikes)
        conditions = self._normalize_list(profile.health_conditions)
        goal = (profile.goal or "").lower()
        diet_type = (profile.diet_type or "").lower()

        return [
            self._apply_personal_rules(
                item=item,
                remaining_calories=remaining,
                allergies=allergies,
                dislikes=dislikes,
                conditions=conditions,
                goal=goal,
                diet_type=diet_type,
            )
            for item in items
        ]

    def _apply_personal_rules(self, item, remaining_calories, allergies, dislikes, conditions, goal, diet_type):
        name = (item.get("name") or "").lower()

        warnings = []
        additions = []
        reductions = []
        replacements = []

        if any(x in name for x in allergies):
            warnings.append("This may conflict with your allergy profile. Avoid this item.")

        if any(x in name for x in dislikes):
            reductions.append("You marked similar foods as disliked.")

        if diet_type == "vegetarian" and any(x in name for x in ["chicken", "fish", "mutton", "meat"]):
            warnings.append("This may not match your vegetarian preference.")

        if diet_type == "vegan" and any(x in name for x in ["milk", "paneer", "cheese", "curd", "yogurt", "egg"]):
            warnings.append("This may not match your vegan preference.")

        item_calories = float(item.get("calories", 0.0))
        fats = float(item.get("fats", 0.0))
        carbs = float(item.get("carbs", 0.0))
        protein = float(item.get("protein", 0.0))
        sugar = float(item.get("sugar", 0.0))
        sodium = float(item.get("sodium", 0.0))
        sat_fat = float(item.get("saturatedFat", 0.0))
        fiber = float(item.get("fiber", 0.0))

        if remaining_calories > 0 and item_calories > remaining_calories and item_calories > 0:
            reductions.append(f"This food may exceed your remaining calorie budget ({int(remaining_calories)} kcal left today).")
            replacements.append("Choose a smaller portion or a lighter alternative.")

        if "lose" in goal:
            if item_calories > 250:
                reductions.append("Reduce portion size to support your weight-loss goal.")
            if fats > 12:
                replacements.append("Replace with a grilled, less oily, or lower-fat option.")
            if fiber < 3 and item_calories > 0:
                additions.append("Add vegetables or salad to improve fullness and fiber.")

        if "gain" in goal or "muscle" in goal:
            if protein < 12 and item_calories > 0:
                additions.append("Add a higher-protein side like eggs, paneer, curd, lentils, or chicken.")

        lower_conditions = [c.lower() for c in conditions]

        if any("diabetes" in c for c in lower_conditions):
            if carbs > 25 or sugar > 8:
                reductions.append("High carb or sugar foods may need portion control for diabetes management.")
            if fiber < 3 and item_calories > 0:
                additions.append("Add fiber-rich foods to slow glucose absorption.")

        if any("blood pressure" in c for c in lower_conditions) or any("hypertension" in c for c in lower_conditions):
            if sodium > 300:
                reductions.append("This may be high in sodium. Reduce portion or choose a lower-salt option.")

        if any("cholesterol" in c for c in lower_conditions):
            if sat_fat > 4 or fats > 15:
                replacements.append("Replace with a lower saturated-fat version.")

        if any("pcos" in c for c in lower_conditions):
            if carbs > 30 and fiber < 3:
                reductions.append("Refined or high-carb foods may need moderation for PCOS.")
            if item_calories > 0:
                additions.append("Add protein and fiber to make this meal more balanced.")

        existing_tip = item.get("pro_tip", "") or ""
        existing_alt = item.get("healthier_alternative", "") or ""

        tip_parts = []
        if warnings:
            tip_parts.extend(warnings)
        if reductions:
            tip_parts.append("Reduce: " + " ".join(reductions))
        if additions:
            tip_parts.append("Add: " + " ".join(additions))

        alt_parts = []
        if replacements:
            alt_parts.append("Replace: " + " ".join(replacements))

        item["pro_tip"] = " ".join([p for p in [existing_tip] + tip_parts if p]).strip()[:500]
        item["healthier_alternative"] = " ".join([p for p in [existing_alt] + alt_parts if p]).strip()[:400]
        return item

    def _normalize_list(self, value):
        if isinstance(value, list):
            return [str(x).strip().lower() for x in value if str(x).strip()]
        if isinstance(value, str):
            return [x.strip().lower() for x in value.split(",") if x.strip()]
        return []

    def _normalize_text_list(self, value):
        if not value:
            return []
        return [x.strip().lower() for x in str(value).split(",") if x.strip()]
