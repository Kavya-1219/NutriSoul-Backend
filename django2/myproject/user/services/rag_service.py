"""
NutriSoul RAG Service
Retrieval-Augmented Generation engine using TF-IDF + cosine similarity
for knowledge retrieval, plus personal user data retrieval from the DB.
"""

import math
import re
import logging
from collections import Counter
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


class NutriSoulRAGService:
    """Lightweight RAG service using TF-IDF for nutrition knowledge retrieval."""

    def __init__(self):
        from .rag_knowledge_base import NUTRITION_KNOWLEDGE_BASE
        self.documents = NUTRITION_KNOWLEDGE_BASE
        self._idf_cache = {}
        self._doc_vectors = []
        self._build_index()

    # ── Index Building ───────────────────────────────────────────────────

    def _tokenize(self, text):
        """Lowercase tokenization with basic stemming-like normalization."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        # Remove very short tokens and common stop words
        stop_words = {
            'the', 'is', 'in', 'a', 'an', 'and', 'or', 'for', 'to', 'of',
            'with', 'on', 'at', 'by', 'it', 'as', 'be', 'are', 'was', 'that',
            'this', 'from', 'can', 'your', 'you', 'but', 'not', 'do', 'if',
            'has', 'have', 'will', 'may', 'all', 'its', 'per', 'also', 'more',
        }
        return [t for t in tokens if len(t) > 1 and t not in stop_words]

    def _build_index(self):
        """Pre-compute TF-IDF vectors for all documents."""
        # Combine title + content + tags for each document
        doc_texts = []
        for doc in self.documents:
            combined = f"{doc['title']} {doc['content']} {' '.join(doc.get('tags', []))}"
            doc_texts.append(combined)

        # Tokenize all docs
        all_doc_tokens = [self._tokenize(text) for text in doc_texts]

        # Build document frequency
        num_docs = len(all_doc_tokens)
        df = Counter()
        for tokens in all_doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                df[token] += 1

        # Compute IDF
        self._idf_cache = {
            term: math.log((num_docs + 1) / (freq + 1)) + 1
            for term, freq in df.items()
        }

        # Compute TF-IDF vectors for each document
        self._doc_vectors = []
        for tokens in all_doc_tokens:
            tf = Counter(tokens)
            total = len(tokens) if tokens else 1
            vector = {
                term: (count / total) * self._idf_cache.get(term, 1.0)
                for term, count in tf.items()
            }
            self._doc_vectors.append(vector)

    def _cosine_similarity(self, vec_a, vec_b):
        """Compute cosine similarity between two sparse vectors (dicts)."""
        # Intersection of keys
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0

        dot_product = sum(vec_a[k] * vec_b[k] for k in common_keys)
        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)

    # ── Knowledge Retrieval ──────────────────────────────────────────────

    def retrieve(self, query, top_k=3):
        """
        Retrieve the top-k most relevant knowledge documents for a query.
        Returns a list of dicts with 'title', 'content', and 'score'.
        """
        if not query or not query.strip():
            return []

        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Build query TF-IDF vector
        tf = Counter(query_tokens)
        total = len(query_tokens)
        query_vector = {
            term: (count / total) * self._idf_cache.get(term, 1.0)
            for term, count in tf.items()
        }

        # Tag boost: if any query token matches a document's tags, boost score
        query_token_set = set(query_tokens)

        # Score all documents
        scored_docs = []
        for i, doc_vector in enumerate(self._doc_vectors):
            score = self._cosine_similarity(query_vector, doc_vector)

            # Tag overlap boost (up to 0.2 bonus)
            doc_tags = set(self.documents[i].get('tags', []))
            tag_overlap = len(query_token_set & doc_tags)
            if tag_overlap > 0:
                score += 0.2 * min(tag_overlap / max(len(doc_tags), 1), 1.0)

            if score > 0.01:  # Minimum threshold
                scored_docs.append({
                    'title': self.documents[i]['title'],
                    'content': self.documents[i]['content'],
                    'score': round(score, 4)
                })

        # Sort by score descending and return top-k
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        return scored_docs[:top_k]

    # ── Personal Data Retrieval ──────────────────────────────────────────

    def get_user_context(self, user):
        """
        Pull the user's live data from the database for personalization.
        Returns a formatted string summarizing their recent activity.
        """
        from ..models import FoodLog, DailyMealPlan, DailyMealEntry, SleepLog, UserProfile
        from django.db.models import Sum, F, FloatField

        context_parts = []
        today = timezone.localtime(timezone.now()).date()

        # 1. Today's food intake
        try:
            food_logs_today = FoodLog.objects.filter(
                user=user,
                timestamp__date=today
            )
            if food_logs_today.exists():
                totals = food_logs_today.aggregate(
                    total_cal=Sum(F('calories_per_unit') * F('quantity'), output_field=FloatField()),
                    total_protein=Sum(F('protein_per_unit') * F('quantity'), output_field=FloatField()),
                    total_carbs=Sum(F('carbs_per_unit') * F('quantity'), output_field=FloatField()),
                    total_fats=Sum(F('fats_per_unit') * F('quantity'), output_field=FloatField()),
                )
                food_names = list(food_logs_today.values_list('name', flat=True))
                context_parts.append(
                    f"Today's Food Intake: {int(totals['total_cal'] or 0)} kcal consumed so far "
                    f"(Protein: {int(totals['total_protein'] or 0)}g, "
                    f"Carbs: {int(totals['total_carbs'] or 0)}g, "
                    f"Fats: {int(totals['total_fats'] or 0)}g). "
                    f"Foods eaten today: {', '.join(food_names[:10])}."
                )
            else:
                context_parts.append("Today's Food Intake: No food logged yet today.")
        except Exception as e:
            logger.error(f"RAG: Error fetching food logs: {e}")

        # 2. Weekly nutrition average (last 7 days)
        try:
            week_start = today - timedelta(days=6)
            food_logs_week = FoodLog.objects.filter(
                user=user,
                timestamp__date__range=[week_start, today]
            )
            if food_logs_week.exists():
                weekly_totals = food_logs_week.aggregate(
                    total_cal=Sum(F('calories_per_unit') * F('quantity'), output_field=FloatField()),
                    total_protein=Sum(F('protein_per_unit') * F('quantity'), output_field=FloatField()),
                )
                days_logged = food_logs_week.values('timestamp__date').distinct().count()
                if days_logged > 0:
                    avg_cal = int((weekly_totals['total_cal'] or 0) / days_logged)
                    avg_protein = int((weekly_totals['total_protein'] or 0) / days_logged)
                    context_parts.append(
                        f"Weekly Averages ({days_logged} days logged): "
                        f"~{avg_cal} kcal/day, ~{avg_protein}g protein/day."
                    )
        except Exception as e:
            logger.error(f"RAG: Error fetching weekly data: {e}")

        # 3. Today's meal plan
        try:
            meal_plan = DailyMealPlan.objects.filter(user=user, date=today).first()
            if meal_plan:
                entries = DailyMealEntry.objects.filter(daily_meal_plan=meal_plan)
                if entries.exists():
                    plan_items = []
                    for entry in entries:
                        status_str = "✅ eaten" if entry.is_eaten else "⬜ not yet"
                        plan_items.append(
                            f"{entry.meal_type}: {entry.title} ({entry.calories} kcal) [{status_str}]"
                        )
                    context_parts.append(
                        f"Today's Meal Plan (target: {meal_plan.target_calories} kcal): "
                        + "; ".join(plan_items) + "."
                    )
        except Exception as e:
            logger.error(f"RAG: Error fetching meal plan: {e}")

        # 4. Recent sleep data
        try:
            recent_sleep = SleepLog.objects.filter(user=user).order_by('-date')[:3]
            if recent_sleep.exists():
                sleep_entries = []
                for log in recent_sleep:
                    sleep_entries.append(
                        f"{log.date}: {log.duration} ({log.quality} quality)"
                    )
                avg_minutes = sum(s.duration_minutes for s in recent_sleep) / recent_sleep.count()
                context_parts.append(
                    f"Recent Sleep (last {recent_sleep.count()} nights): "
                    + "; ".join(sleep_entries)
                    + f". Average: {avg_minutes / 60:.1f} hours/night."
                )
        except Exception as e:
            logger.error(f"RAG: Error fetching sleep data: {e}")

        # 5. Water intake
        try:
            profile = UserProfile.objects.filter(user=user).first()
            if profile and profile.todays_water_intake > 0:
                context_parts.append(
                    f"Today's Water Intake: {profile.todays_water_intake} glasses."
                )
        except Exception as e:
            logger.error(f"RAG: Error fetching water data: {e}")

        return "\n".join(context_parts) if context_parts else "No recent activity data available."

    # ── Prompt Assembly ──────────────────────────────────────────────────

    def build_rag_prompt(self, user_message, user_profile=None, user=None):
        """
        Build the full RAG-augmented prompt combining:
        1. System instructions
        2. Retrieved knowledge documents
        3. User profile
        4. Personal data from DB
        5. User's question
        """

        # 1. Retrieve relevant knowledge
        retrieved_docs = self.retrieve(user_message, top_k=3)
        knowledge_section = ""
        if retrieved_docs:
            knowledge_parts = []
            for doc in retrieved_docs:
                knowledge_parts.append(f"### {doc['title']}\n{doc['content']}")
            knowledge_section = (
                "## Nutrition Knowledge Base (use this information to answer accurately):\n\n"
                + "\n\n".join(knowledge_parts)
            )

        # 2. User profile context
        profile_section = ""
        if user_profile:
            name = user_profile.full_name or "the user"
            weight = f"{user_profile.weight}kg" if user_profile.weight else "unknown"
            height = f"{user_profile.height}cm" if user_profile.height else "unknown"
            age = user_profile.age or "unknown"
            goal = user_profile.goal or "general health"
            diet_type = user_profile.diet_type or "not specified"
            activity = user_profile.activity_level or "not specified"
            allergies = user_profile.food_allergies or "none"
            conditions = user_profile.health_conditions or "none"
            target_cal = user_profile.target_calories or "not calculated"
            bmi = f"{user_profile.calculate_bmi():.1f}" if user_profile.weight and user_profile.height else "not calculated"

            profile_section = f"""## User Profile:
- Name: {name}
- Age: {age}
- Weight: {weight}
- Height: {height}
- BMI: {bmi}
- Diet Type: {diet_type}
- Activity Level: {activity}
- Primary Goal: {goal}
- Target Calories: {target_cal} kcal/day
- Food Allergies: {allergies}
- Health Conditions: {conditions}"""

        # 3. Personal data context
        personal_data_section = ""
        if user:
            try:
                personal_data = self.get_user_context(user)
                if personal_data and personal_data != "No recent activity data available.":
                    personal_data_section = f"## User's Recent Activity Data:\n{personal_data}"
            except Exception as e:
                logger.error(f"RAG: Error building personal data context: {e}")

        # 4. Assemble full prompt
        prompt = f"""You are NutriSoul AI, a professional and friendly nutrition and health assistant for the NutriSoul app.
Your responses are powered by a nutrition knowledge base and the user's personal health data.

{knowledge_section}

{profile_section}

{personal_data_section}

## Instructions:
1. Answer using SPECIFIC FACTS from the knowledge base above when relevant. Cite numbers, ranges, and food examples.
2. Personalize advice based on the user's profile (age, weight, goal, diet type, conditions, allergies).
3. If the user asks about their recent food intake, meals, or sleep, reference their ACTUAL DATA from the activity section above.
4. Never recommend foods the user is allergic to.
5. Keep responses concise but comprehensive (2-4 paragraphs max).
6. If it's a medical emergency or serious health concern, advise consulting a healthcare professional.
7. Be warm, supportive, and motivating.

## User's Question:
"{user_message}"

Respond directly and helpfully:"""

        return prompt.strip()
