import os
import django
import google.generativeai as genai

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
import traceback

def test():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("Testing gemini-1.5-flash...")
        resp = model.generate_content("Hello.")
        print(f"Response: {resp.text}")
    except Exception as e:
        print("Error with gemini-1.5-flash:")
        traceback.print_exc()
        
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        print("Testing gemini-2.0-flash...")
        resp = model.generate_content("Hello.")
        print(f"Response: {resp.text}")
    except Exception as e:
        print("Error with gemini-2.0-flash:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
