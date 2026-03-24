import os
import django
import google.generativeai as genai

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing all models...")
try:
    for m in genai.list_models():
        print(f"Name: {m.name}")
        print(f"Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
