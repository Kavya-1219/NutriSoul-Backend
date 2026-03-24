import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None
from django.conf import settings

logger = logging.getLogger(__name__)

class AiAssistantService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.model = None
        self.rag_service = None

        if self.api_key and genai:
            try:
                genai.configure(api_key=self.api_key)
                # Using gemini-2.0-flash for speed and stability
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("AiAssistantService: Gemini AI initialized with model gemini-2.0-flash")
            except Exception as e:
                logger.error(f"AiAssistantService: Failed to initialize Gemini AI: {e}")
        else:
            logger.error("AiAssistantService: GEMINI_API_KEY is not configured in settings.py.")

        # Initialize RAG service
        try:
            from .rag_service import NutriSoulRAGService
            self.rag_service = NutriSoulRAGService()
            logger.info("AiAssistantService: RAG service initialized successfully.")
        except Exception as e:
            logger.error(f"AiAssistantService: Failed to initialize RAG service: {e}")

    def get_chat_response(self, user_message, user_profile=None, user=None):
        if not self.model:
            return "I'm sorry, my AI brain is currently offline. Please try again later."

        try:
            # Use RAG-augmented prompt if available, otherwise fallback to basic prompt
            if self.rag_service:
                prompt = self.rag_service.build_rag_prompt(user_message, user_profile, user)
                logger.info("AiAssistantService: Using RAG-augmented prompt.")
            else:
                prompt = self._build_chat_prompt(user_message, user_profile)
                logger.info("AiAssistantService: RAG unavailable, using basic prompt.")

            response = self.model.generate_content(prompt)
            return getattr(response, "text", "") or "I'm not sure how to respond to that. Could you rephrase?"
        except Exception as e:
            logger.exception(f"AiAssistantService: Error generating chat response: {e}")
            return f"I encountered an error while thinking: {str(e)[:50]}..."

    def _build_chat_prompt(self, user_message, user_profile):
        """Legacy prompt builder — used as fallback when RAG is unavailable."""
        context = ""
        if user_profile:
            name = user_profile.full_name or "the user"
            weight = f"{user_profile.weight}kg" if user_profile.weight else "unknown"
            height = f"{user_profile.height}cm" if user_profile.height else "unknown"
            age = user_profile.age or "unknown"
            goal = user_profile.goal or "general health"
            allergies = user_profile.food_allergies or "none"
            conditions = user_profile.health_conditions or "none"
            
            context = f"""
User Profile:
- Name: {name}
- Age: {age}
- Weight: {weight}
- Height: {height}
- Primary Goal: {goal}
- Food Allergies: {allergies}
- Health Conditions: {conditions}

"""

        system_prompt = f"""
You are NutriSoul AI, a professional and friendly nutrition and health assistant for the NutriSoul app.
Your goal is to provide accurate, helpful, and motivating advice based on the user's profile and queries.

{context}
Instructions:
1. Always be supportive and professional.
2. If the user asks about their specific progress (weight, calories, etc.), refer to their profile data if available.
3. If suggested meals, consider their allergies and health conditions.
4. Keep responses concise but comprehensive.
5. If you don't know something or it's a medical emergency, advise the user to consult a healthcare professional.
6. The user just said: "{user_message}"

Respond directly to the user message.
""".strip()
        return system_prompt
