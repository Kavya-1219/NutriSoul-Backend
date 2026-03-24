import os
import django
import json
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from unittest.mock import patch

def test_food_scan():
    client = Client()
    
    # 1. Create/Get test user
    user, created = User.objects.get_or_create(username='tester@example.com', email='tester@example.com')
    client.force_login(user)
    
    # Create a dummy image
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    dummy_image = SimpleUploadedFile("test_cake.jpg", image_content, content_type="image/jpeg")

    print("--- Testing Food Scan (Authenticated) ---")
    
    # Mocking the AI service to avoid real network calls during test
    mock_detected_items = [
        {
            "name": "Cake",
            "calories": 389.0,
            "protein": 5.0,
            "carbs": 56.0,
            "fats": 17.0,
            "servingQuantity": 100.0,
            "servingUnit": "g",
            "confidence": 0.82
        }
    ]

    with patch('user.services.FoodScanService.scan_food') as mock_scan:
        mock_scan.return_value = (mock_detected_items, "success")
        
        response = client.post(
            '/api/food-scan/', 
            data={'image': dummy_image, 'text': 'A slice of cake'},
            format='multipart'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        assert response.status_code == 200
        assert response.json()['message'] == "success"
        assert len(response.json()['detected_items']) == 1
        assert response.json()['detected_items'][0]['name'] == "Cake"

    print("\nFood Scan API Test Passed (Mocked AI)!")

if __name__ == "__main__":
    test_food_scan()
    
    print("\nTo test with real AI, make sure to:")
    print("1. Set GEMINI_API_KEY in myproject/settings.py")
    print("2. pip install google-generativeai pillow")
    print("3. Run: curl.exe -X POST http://127.0.0.1:8000/api/food-scan/ -H 'Authorization: Token YOUR_TOKEN' -F 'image=@path/to/img.jpg'")
