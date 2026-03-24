import os
import google.generativeai as genai
from dotenv import load_dotenv
import typing as t
import json

load_dotenv('c:/Users/vkavy/OneDrive/Desktop/frontend_backend/django2/myproject/.env')
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

models_to_test = [
    "non-existent-model", 
    "gemini-2.0-flash", # Known to be 429
    "gemini-1.5-flash-latest" # Known to work
]

for model_name in models_to_test:
    try:
        print(f"Testing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("hi")
        print(f"Success with {model_name}: {response.text}")
        break
    except Exception as e:
        err_msg = str(e).lower()
        print(f"Model {model_name} failed: {err_msg}")
        if "403" in err_msg:
            print("Stopping due to 403")
            break
        continue
