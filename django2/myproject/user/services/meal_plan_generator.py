import random
import json
import logging
import google.generativeai as genai
from datetime import date, timedelta
from django.db import transaction
from django.conf import settings
from ..models import MealTemplate, MealTemplateItem, DailyMealPlan, DailyMealEntry, UserProfile

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

    def generate_daily_plan_for_user(self, user, seed, force_refresh=False, target_date=None):
        if not target_date:
            target_date = date.today()
        
        with transaction.atomic():
            if not force_refresh:
                # Use select_for_update to handle race conditions during generation
                plan = DailyMealPlan.objects.filter(user=user, date=target_date).first()
                if plan:
                    return plan

            # Delete old plan if refreshing
            DailyMealPlan.objects.filter(user=user, date=target_date).delete()

            profile = UserProfile.objects.filter(user=user).select_related('user').first()
            target_calories = profile.calculate_calorie_goal() if profile else 2000
            
            try:
                plan = DailyMealPlan.objects.create(
                    user=user,
                    date=target_date,
                    target_calories=target_calories
                )
            except Exception as e:
                # Fallback if another thread just created it
                logger.error(f"Failed to create plan, trying to fetch: {e}")
                plan = DailyMealPlan.objects.filter(user=user, date=target_date).first()
                if plan:
                    return plan
                raise e

            # Respect meals_per_day
            meal_types = ['breakfast', 'lunch', 'dinner']
            if profile and profile.meals_per_day and profile.meals_per_day >= 4:
                meal_types.append('snack')
            
            rng = random.Random(seed)
            for m_type in meal_types:
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
            # 1. Filter by diet type (Strict Enforcement)
            if profile.diet_type == 'Vegan':
                # Vegan: No meat, no egg, no dairy
                templates = templates.exclude(diet_type__icontains='nonveg')
                templates = templates.exclude(diet_type__icontains='eggetarian')
                templates = templates.exclude(title__icontains='egg')
                templates = templates.exclude(title__icontains='milk')
                templates = templates.exclude(title__icontains='cheese')
                templates = templates.exclude(title__icontains='butter')
                templates = templates.exclude(title__icontains='yogurt')
                templates = templates.exclude(title__icontains='dairy')
            elif profile.diet_type == 'Vegetarian':
                # Vegetarian: No meat, no egg
                templates = templates.exclude(diet_type__icontains='nonveg')
                templates = templates.exclude(diet_type__icontains='eggetarian')
                templates = templates.exclude(title__icontains='egg')
            elif profile.diet_type == 'Eggetarian':
                # Eggetarian: No meat (can have egg/dairy)
                templates = templates.exclude(diet_type__icontains='nonveg')
            
            # 2. Filter by Allergies AND Dislikes (Strict Exclusion)
            # Combine food_allergies (JSON), allergies (JSON), and dislikes (JSON)
            all_exclusions = set()
            for field in [profile.food_allergies, profile.allergies, profile.dislikes, profile.health_conditions]:
                if isinstance(field, list):
                    all_exclusions.update([str(a).lower().strip() for a in field if a])
                elif isinstance(field, str):
                    all_exclusions.update([a.strip().lower() for a in field.split(',') if a.strip()])
            
            # Add legacy food_dislikes
            if profile.food_dislikes:
                all_exclusions.update([a.strip().lower() for a in profile.food_dislikes.split(',') if a.strip()])

            if all_exclusions:
                from django.db.models import Q
                import operator
                from functools import reduce
                
                # 1. Exclude templates where Title matches
                title_exclusion_queries = [Q(title__icontains=ing) for ing in all_exclusions]
                if title_exclusion_queries:
                    templates = templates.exclude(reduce(operator.or_, title_exclusion_queries))
                
                # 2. Exclude templates where any ITEM Name matches
                # We do this by getting the IDs of templates that have at least one bad item
                bad_item_template_ids = MealTemplateItem.objects.filter(
                    reduce(operator.or_, [Q(name__icontains=ing) for ing in all_exclusions])
                ).values_list('meal_template_id', flat=True)
                
                templates = templates.exclude(id__in=bad_item_template_ids)

            # 3. Enhanced: Recent Meal Avoidance (7 days for more variety)
            recent_ids = DailyMealEntry.objects.filter(
                daily_meal_plan__user=user,
                daily_meal_plan__date__gte=date.today() - timedelta(days=7)
            ).values_list("meal_template_id", flat=True)
            
            # Try to exclude recent meals, but keep at least 5 options if possible
            # We don't want to show empty list just because of variety
            templates_no_recent = templates.exclude(id__in=recent_ids)
            if templates_no_recent.count() >= 5:
                templates = templates_no_recent
            elif templates.count() == 0:
                # If everything was excluded by allergies/diet, we might have 0.
                # In that case, we MUST NOT return anything that violates allergies.
                # But we can try to relax diet type if it's too strict (ONLY if not allergy)
                pass

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
                # 30% tolerance to ensure we have enough variety (up to 20 swaps)
                min_cal = target * 0.7
                max_cal = target * 1.3
                
                # Filter by calorie range
                balanced = templates.filter(calories__gte=min_cal, calories__lte=max_cal)
                if balanced.exists():
                    templates = balanced

        # Increase limit to 50 to allow up to 20 swaps reliably
        return templates.order_by('?')[:50]

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
            all_exclusions = set()
            for field in [profile.food_allergies, profile.allergies, profile.dislikes, profile.health_conditions]:
                if isinstance(field, list):
                    all_exclusions.update([str(a).lower().strip() for a in field if a])
                elif isinstance(field, str):
                    all_exclusions.update([a.strip().lower() for a in field.split(',') if a.strip()])
            if profile.food_dislikes:
                all_exclusions.update([a.strip().lower() for a in profile.food_dislikes.split(',') if a.strip()])
                
            if any(excl in template.title.lower() for excl in all_exclusions):
                 return None, "Selected meal contains items you are allergic to or dislike."
            
            from django.db.models import Q
            import operator
            from functools import reduce
            bad_items = template.items.filter(
                reduce(operator.or_, [Q(name__icontains=excl) for excl in all_exclusions])
            ) if all_exclusions else []
            if bad_items:
                return None, "Selected meal contains ingredients you are allergic to or dislike."

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
