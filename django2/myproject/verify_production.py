import os
import django
import sys
import json
from unittest.mock import MagicMock

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.services import FoodScanService
from user.models import FoodItem
import PIL.Image

def verify_production_flow():
    service = FoodScanService()
    service.model = MagicMock()
    PIL.Image.open = MagicMock()
    
    print("\n--- TEST 1: Visual Detection + DB Match (Pizza) ---")
    # Mock Gemini identifying Pizza
    mock_response = MagicMock()
    mock_response.text = '{"items": [{"name": "Pizza", "confidence": 0.9}]}'
    service.model.generate_content.return_value = mock_response
    
    results, message = service.scan_food("dummy_image.jpg")
    print(f"Message: {message}")
    print(f"Results: {json.dumps(results, indent=2)}")
    
    if results and results[0]['name'] == 'Pizza' and results[0]['calories'] == 266.0:
        print("SUCCESS: Matched Pizza from DB")
    else:
        print("FAILURE: Did not match Pizza correctly from DB")

    print("\n--- TEST 2: Visual Detection + AI Estimate (Sushi - not in DB) ---")
    mock_response.text = '{"items": [{"name": "Sushi", "confidence": 0.85, "estimated_per_100g": {"calories": 150, "protein": 5, "carbs": 30, "fats": 1}}]}'
    results, message = service.scan_food("dummy_image.jpg")
    print(f"Results: {json.dumps(results, indent=2)}")
    
    if results and results[0]['name'] == 'Sushi' and results[0].get('calories') == 150:
        print("SUCCESS: Used AI estimate for Sushi")
    else:
        print("FAILURE: Did not use AI estimate correctly")

    print("\n--- TEST 3: Professional Quota error ---")
    service.model.generate_content.side_effect = Exception("User quota exceeded")
    results, message = service.scan_food("dummy_image.jpg")
    print(f"Message: {message}")
    if message == "AI service temporarily unavailable. Please try again later.":
        print("SUCCESS: Professional quota error message returned")
    else:
        print("FAILURE: Unexpected quota error message")

if __name__ == "__main__":
    verify_production_flow()
