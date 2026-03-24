import os
import django
import google.generativeai as genai
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

def debug_gemini_scan():
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    print(f"Using API Key: {api_key[:10]}...")
    
    if not api_key or 'YOUR_GEMINI_API_KEY' in api_key:
        print("ERROR: API Key not set correctly in settings.py")
        return

    genai.configure(api_key=api_key)
    
    print("\nAvailable models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    model_name = 'gemini-1.5-pro'
    print(f"\nTrying model: {model_name}")
    model = genai.GenerativeModel(model_name)
    
    try:
        # Test text-only generation first
        resp = model.generate_content("Hello, identify 'Apple' in JSON format.")
        print(f"Raw Response Text: {resp.text}")
    except Exception as e:
        print(f"ERROR during AI call with {model_name}: {str(e)}")
        
        # Try with models/ prefix
        alt_model_name = f"models/{model_name}"
        print(f"\nTrying alternative model name: {alt_model_name}")
        try:
            model_alt = genai.GenerativeModel(alt_model_name)
            resp = model_alt.generate_content("Hello, identify 'Apple' in JSON format.")
            print(f"Raw Response (with prefix): {resp.text}")
        except Exception as e2:
            print(f"ERROR during AI call with {alt_model_name}: {str(e2)}")

if __name__ == "__main__":
    debug_gemini_scan()
