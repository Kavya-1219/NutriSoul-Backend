import json
import logging
import re
import requests

import google.generativeai as genai
from PIL import Image
from django.conf import settings

from ..models import FoodItem

logger = logging.getLogger(__name__)


class FoodScanService:
    BLACKLIST = {
        "textile", "wool", "toy", "fabric", "clothing", "pattern", "product",
        "person", "human", "furniture", "table", "bottle", "wrapper", "background",
        "plate", "dish", "bowl", "spoon", "fork", "knife", "utensil", "cutlery",
        "hand", "finger", "countertop", "floor", "wall", "window"
    }

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.model = None

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            logger.error("GEMINI_API_KEY is not configured.")

        # Developer Mock Mode (Allows testing without hitting API quotas)
        self.mock_mode = getattr(settings, "GEMINI_MOCK_MODE", False)
        
        self.edamam_app_id = getattr(settings, "EDAMAM_APP_ID", None)
        self.edamam_api_key = getattr(settings, "EDAMAM_API_KEY", None)

    def scan_food(self, image_file, additional_text=""):
        if not self.model:
            return [], "AI service unavailable"

        try:
            img = Image.open(image_file).convert("RGB")
            
            if self.mock_mode:
                logger.info("GEMINI_MOCK_MODE is ON. Returning simulated response.")
                raw_text = '{"items": [{"name": "Pizza", "confidence": 0.92, "estimated_per_100g": {"calories": 266, "protein": 11, "carbs": 33, "fats": 10}}]}'
            else:
                prompt = self._build_prompt(additional_text)
                response = self.model.generate_content([prompt, img])
                raw_text = getattr(response, "text", "") or ""
            
            logger.info("Raw Gemini response: %s", raw_text)
            cleaned_text = self._extract_json_text(raw_text)

            if not cleaned_text:
                return [], "No confident food detected"

            data = json.loads(cleaned_text)
            detected_items = data.get("items", [])
            
            if not isinstance(detected_items, list) or not detected_items:
                return [], "No confident food detected"

            results = []
            for item in detected_items:
                # 1. Main visual detection happens here
                # 2. Strict DB matching happens inside _map_item_to_result
                mapped = self._map_item_to_result(item)
                if mapped:
                    results.append(mapped)

            if not results:
                return [], "No confident food detected"

            # 3. Exact response format for success
            return results, "success"

        except Exception as e:
            error_text = str(e).lower()
            logger.exception("Gemini scan failed: %s", error_text)

            # Professional Quota/Rate Limit Error Handling
            if any(x in error_text for x in ["quota", "resource exhausted", "429", "rate limit"]):
                return [], "AI service temporarily unavailable. Please try again later."

            if "not found" in error_text:
                return [], "AI model configuration error."
            
            return [], "AI service encountered an error"

    def _build_prompt(self, additional_text=""):
        prompt = """
You are identifying foods from an image.

Return ONLY valid JSON.
Do not include markdown fences.
Do not include explanation text.

Return this exact structure:
{
  "items": [
    {
      "name": "food name",
      "confidence": 0.0,
      "estimated_per_100g": {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fats": 0.0
      }
    }
  ]
}

Rules:
- Identify only food or drink items actually visible in the image.
- Common valid items include apple, banana, salad, cucumber, tomato, rice, cake, pizza, burger, chocolate, milk, tea, coffee, juice, noodles, fruit, vegetables.
- Ignore non-food items like people, furniture, table, bottle, wrapper, textile, toy, fabric, background.
- If no food or drink is confidently visible, return:
  {"items": []}
- Confidence should be between 0.0 and 1.0.
- If macros are estimated, provide reasonable approximate values per 100g.
""".strip()

        if additional_text:
            prompt += f"\nUser context: {additional_text.strip()}"

        prompt += "\n\nAlso ensure the response format remains exactly as specified in the rules, focusing on identified food items."
        return prompt

    def _extract_json_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.strip()

        # Remove markdown fences if present
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        # Extract first JSON object if extra text exists
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return ""

        return text[start:end + 1].strip()

    def _map_item_to_result(self, item: dict):
        if not isinstance(item, dict):
            return None

        name = (item.get("name") or "").strip()
        if not name:
            return None

        name_lower = name.lower()

        # Reject only obvious junk
        if name_lower in self.BLACKLIST:
            logger.info("Skipping blacklisted label: %s", name)
            return None

        confidence = item.get("confidence", 0.7)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.7

        # Filter out very low confidence overall, or low-confidence potential junk
        if confidence < 0.2:
            logger.info("Skipping low-confidence item: %s (conf=%s)", name, confidence)
            return None

        if confidence < 0.4 and name_lower in self.BLACKLIST:
            logger.info("Skipping low-confidence potential junk: %s (conf=%s)", name, confidence)
            return None

        logger.info("Attempting DB match for name: %s", name)
        db_food = self._find_food_match(name)

        if db_food:
            logger.info("Matched DB food: input=%s db=%s", name, db_food.name)
            return {
                "name": db_food.name,
                "calories": float(db_food.calories_per_100g),
                "protein": float(db_food.protein_per_100g),
                "carbs": float(db_food.carbs_per_100g),
                "fats": float(db_food.fats_per_100g),
                "servingQuantity": float(db_food.serving_quantity),
                "servingUnit": db_food.serving_unit,
                "confidence": confidence,
            }

        # Fallback to Edamam API
        edamam_data = self._fetch_edamam_nutrition(name)
        if edamam_data:
            logger.info("Matched Edamam food: input=%s", name)
            edamam_data["confidence"] = confidence
            return edamam_data

        est = item.get("estimated_per_100g") or {}

        logger.info("No DB match. Using AI estimate for: %s", name)
        return {
            "name": name,
            "calories": self._safe_float(est.get("calories"), 0.0),
            "protein": self._safe_float(est.get("protein"), 0.0),
            "carbs": self._safe_float(est.get("carbs"), 0.0),
            "fats": self._safe_float(est.get("fats"), 0.0),
            "servingQuantity": 100.0,
            "servingUnit": "g",
            "confidence": confidence,
        }

    def _find_food_match(self, name: str):
        name = name.strip()
        if not name:
            return None

        # 1. Exact case-insensitive match
        exact = FoodItem.objects.filter(name__iexact=name).first()
        if exact:
            logger.info("Found exact DB match: %s", exact.name)
            return exact

        # 2. Singular/plural normalization
        normalized = name.lower().strip()
        candidates = {normalized}
        if normalized.endswith("s"):
            candidates.add(normalized[:-1])
        else:
            candidates.add(normalized + "s")

        for candidate in candidates:
            match = FoodItem.objects.filter(name__iexact=candidate).first()
            if match:
                logger.info("Found normalized DB match: %s -> %s", candidate, match.name)
                return match

        # 3. Only use whole important words (min 4 chars), not broad icontains
        words = [w.lower() for w in re.findall(r"[A-Za-z]+", name) if len(w) >= 4]
        for word in words:
            if word in self.BLACKLIST:
                continue

            # Strict word match
            match = FoodItem.objects.filter(name__iexact=word).first()
            if match:
                logger.info("Found strict word DB match: %s -> %s", word, match.name)
                return match

        logger.info("No safe DB match found for: %s", name)
        return None

    def _safe_float(self, value, default=0.0):
        try:
            return float(value)
        except Exception:
            return default

    def _fetch_edamam_nutrition(self, query: str):
        if not self.edamam_app_id or not self.edamam_api_key or self.edamam_app_id == 'your_edamam_app_id':
            return None

        try:
            url = "https://api.edamam.com/api/food-database/v2/parser"
            params = {
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_api_key,
                "ingr": query,
                "nutrition-type": "logging"
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if "hints" in data and len(data["hints"]) > 0:
                food = data["hints"][0]["food"]
                nutrients = food.get("nutrients", {})
                
                return {
                    "name": food.get("label", query),
                    "calories": float(nutrients.get("ENERC_KCAL", 0.0)),
                    "protein": float(nutrients.get("PROCNT", 0.0)),
                    "carbs": float(nutrients.get("CHOCDF", 0.0)),
                    "fats": float(nutrients.get("FAT", 0.0)),
                    "servingQuantity": 100.0,
                    "servingUnit": "g",
                }
        except Exception as e:
            logger.warning("Edamam API fallback failed: %s", e)
        
        return None

    def _fallback_from_filename(self, image_file):
        import os
        import re

        filename = getattr(image_file, "name", "") or ""
        base = os.path.splitext(os.path.basename(filename))[0].lower()
        logger.info("Filename fallback starting for base='%s'", base)

        # Extract words of 3+ chars
        words = [w for w in re.findall(r"[a-zA-Z]+", base) if len(w) >= 3]
        logger.info("Extracted filename keywords: %s", words)

        for word in words:
            if word in self.BLACKLIST:
                continue
                
            db_food = self._find_food_match(word)
            if db_food:
                logger.info("Filename fallback MATCH FOUND in DB: '%s' -> '%s'", word, db_food.name)
                return [{
                    "name": db_food.name,
                    "calories": float(db_food.calories_per_100g),
                    "protein": float(db_food.protein_per_100g),
                    "carbs": float(db_food.carbs_per_100g),
                    "fats": float(db_food.fats_per_100g),
                    "servingQuantity": float(db_food.serving_quantity),
                    "servingUnit": db_food.serving_unit,
                    "confidence": 0.6,
                }]

        logger.info("Filename fallback: No DB match found for keywords %s", words)
        return []
