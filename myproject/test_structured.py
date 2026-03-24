import os
import google.generativeai as genai
from dotenv import load_dotenv
import typing as t
import json

load_dotenv('c:/Users/vkavy/OneDrive/Desktop/frontend_backend/django2/myproject/.env')
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("API Key not found!")
    exit(1)

genai.configure(api_key=api_key)

class NutritionSchema(t.TypedDict):
    calories: float
    protein: float
    carbs: float
    fats: float

class FoodItemSchema(t.TypedDict):
    name: str
    confidence: float
    estimated_per_100g: NutritionSchema

class FoodResponseSchema(t.TypedDict):
    items: list[FoodItemSchema]

model_name = "gemini-2.5-flash"

try:
    print(f"Testing model: {model_name} with full structured output")
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=FoodResponseSchema
        )
    )
    
    response = model.generate_content("Analyze an imaginary apple and return nutrition.")
    print(f"Response: {response.text}")
    print(f"Response text: {response.text}")
    print("Parsing JSON...")
    data = json.loads(response.text)
    print(f"Parsed Successfully: {data}")

except Exception as e:
    print(f"Error: {e}")
