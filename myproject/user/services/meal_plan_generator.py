import random
import json
import logging
import google.generativeai as genai
from datetime import date, timedelta
from django.db import transaction
from django.conf import settings
from ..models import MealTemplate, DailyMealPlan, DailyMealEntry, UserProfile

logger = logging.getLogger(__name__)

class MealPlanGenerator:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
        else:
            self.model = None
            logger.error("GEMINI_API_KEY not found in settings.")

    def generate_daily_plan_for_user(self, user, seed, force_refresh=False):
        today = date.today()
        
        with transaction.atomic():
            if not force_refresh:
                plan = DailyMealPlan.objects.filter(user=user, date=today).first()
                if plan:
                    return plan

            # Delete old plan if refreshing
            DailyMealPlan.objects.filter(user=user, date=today).delete()

            profile = UserProfile.objects.filter(user=user).first()
            target_calories = profile.calculate_calorie_goal() if profile else 2000
            bmi = profile.calculate_bmi() if profile else 0
            
            plan = DailyMealPlan.objects.create(
                user=user,
                date=today,
                target_calories=target_calories
            )

            # Try AI selection first
            selected_ids = self._get_ai_selections(profile, bmi, target_calories, seed)
            
            if selected_ids:
                for m_type, template_id in selected_ids.items():
                    template = MealTemplate.objects.filter(id=template_id).first()
                    if template:
                        self._create_entry(plan, m_type, template)
                    else:
                        # Fallback for individual meal if AI returned invalid ID
                        self._fallback_pick(plan, m_type, user, seed)
            else:
                # Full fallback to random if AI failed
                rng = random.Random(seed)
                for m_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                    self._fallback_pick(plan, m_type, user, seed, rng)
            
            return plan

    def _get_ai_selections(self, profile, bmi, target_calories, seed):
        if not self.model or not profile:
            return None

        # Filter pools for AI to choose from
        pools = {}
        for m_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            candidates = self.get_alternatives_for_user(profile.user, m_type, target_calories=target_calories)
            pools[m_type] = [{"id": c.id, "title": c.title, "calories": c.calories, "protein": c.protein} for c in candidates]

        prompt = f"""
User details:
- BMI: {bmi:.1f}
- Goal: {profile.goal}
- Diet: {profile.diet_type}
- Allergies: {profile.food_allergies}
- Health conditions: {profile.health_conditions}
- Target calories: {target_calories}

Choose exactly one breakfast, one lunch, one snack and one dinner from the provided candidate meals.

Candidate Meals:
{json.dumps(pools, indent=2)}

Rules:
1. Do not choose meals containing allergic ingredients.
2. Follow the user's diet type ({profile.diet_type}).
3. Prefer high protein meals if goal is muscle gain.
4. Prefer lower calorie meals if goal is weight loss.
5. Return ONLY a valid JSON object with meal_template_ids.
6. Seed for variety (optional hint): {seed}

Return format:
{{
 "breakfast_id": 12,
 "lunch_id": 44,
 "snack_id": 81,
 "dinner_id": 63
}}
""".strip()

        try:
            response = self.model.generate_content(prompt)
            data = self._extract_json(response.text)
            if data:
                return {
                    "breakfast": data.get("breakfast_id"),
                    "lunch": data.get("lunch_id"),
                    "snack": data.get("snack_id"),
                    "dinner": data.get("dinner_id")
                }
        except Exception as e:
            logger.error(f"AI meal selection failed: {e}")
        
        return None

    def _extract_json(self, text):
        try:
            # Basic JSON extraction from markdown if needed
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text.strip())
        except:
            return None

    def _create_entry(self, plan, m_type, template):
        DailyMealEntry.objects.create(
            daily_meal_plan=plan,
            meal_type=m_type,
            meal_template=template,
            title=template.title,
            calories=template.calories,
            protein=template.protein,
            carbs=template.carbs,
            fats=template.fats
        )

    def _fallback_pick(self, plan, m_type, user, seed, rng=None):
        if not rng:
            rng = random.Random(seed + m_type)
        
        template = self._pick_meal(user, m_type, rng, target_calories=plan.target_calories)
        if template:
            self._create_entry(plan, m_type, template)
        else:
            DailyMealEntry.objects.create(
                daily_meal_plan=plan,
                meal_type=m_type,
                title=f"Custom {m_type.capitalize()}",
                calories=plan.target_calories // 4,
                protein=20,
                carbs=50,
                fats=15
            )

    def get_alternatives_for_user(self, user, meal_type, target_calories=None):
        profile = UserProfile.objects.filter(user=user).first()
        templates = MealTemplate.objects.filter(meal_type=meal_type)

        if profile:
            # 1. Filter by diet type if specified
            if profile.diet_type:
                templates = templates.filter(diet_type__icontains=profile.diet_type)
            
            # 2. Filter by allergies
            allergies = (profile.food_allergies or "").lower().split(',')
            allergies = [a.strip() for a in allergies if a.strip()]
            
            if allergies:
                filtered_ids = []
                for t in templates:
                    text = (t.title).lower()
                    if not any(a in text for a in allergies):
                        filtered_ids.append(t.id)
                templates = templates.filter(id__in=filtered_ids)

            # 3. Enhanced: Recent Meal Avoidance (5 days)
            today = date.today()
            recent_ids = DailyMealEntry.objects.filter(
                daily_meal_plan__user=user,
                daily_meal_plan__date__gte=today - timedelta(days=5)
            ).values_list("meal_template_id", flat=True)
            
            # Exclude only if pool remains large enough
            if templates.exclude(id__in=recent_ids).count() >= 3:
                templates = templates.exclude(id__in=recent_ids)

            # 4. Enhanced: Calorie Distribution (Macro Balancing)
            if target_calories:
                dist = {
                    'breakfast': 0.25,
                    'lunch': 0.35,
                    'snack': 0.10,
                    'dinner': 0.30
                }
                ratio = dist.get(meal_type.lower(), 0.25)
                target = target_calories * ratio
                # 20% tolerance
                min_cal = target * 0.8
                max_cal = target * 1.2
                
                # Filter by calorie range
                balanced = templates.filter(calories__gte=min_cal, calories__lte=max_cal)
                if balanced.exists():
                    templates = balanced

        return templates[:20]

    def swap_meal_for_user(self, user, meal_type, meal_template_id):
        today = date.today()
        plan = DailyMealPlan.objects.filter(user=user, date=today).first()
        if not plan:
            return None, "No meal plan found for today."

        template = MealTemplate.objects.filter(id=meal_template_id).first()
        if not template:
            return None, "Selected meal template not found."

        if template.meal_type != meal_type:
            return None, f"Selected meal is not a {meal_type}."

        profile = UserProfile.objects.filter(user=user).first()
        if profile:
            allergies = (profile.food_allergies or "").lower().split(',')
            allergies = [a.strip() for a in allergies if a.strip()]
            if any(a in template.title.lower() for a in allergies):
                 return None, "Selected meal contains items you are allergic to."

        entry = DailyMealEntry.objects.filter(daily_meal_plan=plan, meal_type=meal_type).first()
        if entry:
            entry.meal_template = template
            entry.title = template.title
            entry.calories = template.calories
            entry.protein = template.protein
            entry.carbs = template.carbs
            entry.fats = template.fats
            entry.save()
            return plan, "success"
        
        return None, "Meal type entry not found in today's plan."

    def _pick_meal(self, user, meal_type, rng, target_calories=None):
        pool = list(self.get_alternatives_for_user(user, meal_type, target_calories=target_calories))
        if not pool:
            return None
        return rng.choice(pool)
