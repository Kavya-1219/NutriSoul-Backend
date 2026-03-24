import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('c:/Users/vkavy/OneDrive/Desktop/frontend_backend/django2/myproject/.env')
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("API Key not found!")
    exit(1)

genai.configure(api_key=api_key)

models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]

for model_name in models_to_test:
    try:
        print(f"Testing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, are you working?")
        print(f"Response from {model_name}: {response.text}")
    except Exception as e:
        print(f"Error with {model_name}: {e}")
