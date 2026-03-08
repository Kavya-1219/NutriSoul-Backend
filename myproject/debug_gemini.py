import os
import django
from PIL import Image
import google.generativeai as genai
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from user.models import FoodItem

def debug_gemini_scan():
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    print(f"Using API Key: {api_key[:10]}...")
    
    if not api_key or 'YOUR_GEMINI_API_KEY' in api_key:
        print("ERROR: API Key not set correctly in settings.py")
        return

    model_name = 'models/gemini-1.5-flash'
    print(f"\nTrying model: {model_name}")
    model = genai.GenerativeModel(model_name)
    
    prompt = """
    Identify food items in an image.
    Return ONLY a valid JSON object:
    {
      "items": [
        {
          "name": "Apple",
          "confidence": 0.95,
          "estimated_per_100g": {
            "calories": 52.0,
            "protein": 0.3,
            "carbs": 14.0,
            "fats": 0.2
          }
        }
      ]
    }
    """
    
    try:
        # Test text-only generation first to verify key/model
        resp = model.generate_content("Hello, identify 'Apple' in JSON format as requested.")
        print(f"Raw Response Text: {resp.text}")
        
        # Verify JSON parsing logic
        content = resp.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        content = content.strip()
        if not content.startswith('{'):
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
        
        data = json.loads(content)
        print(f"Parsed Data: {data}")
        
    except Exception as e:
        print(f"ERROR during AI call: {str(e)}")

if __name__ == "__main__":
    debug_gemini_scan()
