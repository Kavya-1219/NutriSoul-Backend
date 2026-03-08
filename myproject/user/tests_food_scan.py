import sys
from unittest.mock import MagicMock, patch

# Mock Django settings and models before anything else
mock_settings = MagicMock()
mock_settings.GEMINI_API_KEY = "dummy_key"
mock_settings.EDAMAM_APP_ID = "dummy_app_id"
mock_settings.EDAMAM_API_KEY = "dummy_api_key"
sys.modules['django.conf'] = MagicMock()
sys.modules['django.conf'].settings = mock_settings

# Mock user.models
mock_models = MagicMock()
sys.modules['user.models'] = mock_models

# Now we can safely import or mock the rest
import os
import json
import unittest
from PIL import Image
import io

class MockFoodItem:
    def __init__(self, name, cal, pro, carb, fat, qty=100.0, unit='g'):
        self.name = name
        self.calories_per_100g = cal
        self.protein_per_100g = pro
        self.carbs_per_100g = carb
        self.fats_per_100g = fat
        self.serving_quantity = qty
        self.serving_unit = unit

class TestFoodScanServiceLogic(unittest.TestCase):
    def setUp(self):
        # Patching genai
        self.patcher_genai = patch('google.generativeai.configure')
        self.patcher_model = patch('google.generativeai.GenerativeModel')
        self.patcher_image = patch('PIL.Image.open')
        
        self.mock_genai_config = self.patcher_genai.start()
        self.mock_genai_model = self.patcher_model.start()
        self.mock_image_open = self.patcher_image.start()
        
        from user.services import FoodScanService
        self.service = FoodScanService()
        self.service.model = MagicMock()

    def tearDown(self):
        self.patcher_genai.stop()
        self.patcher_model.stop()
        self.patcher_image.stop()

    def test_json_extraction_markdown(self):
        mock_response = MagicMock()
        mock_response.text = '```json\n{"items": [{"name": "Apple", "confidence": 0.9, "estimated_per_100g": {"calories": 52}}]}\n```'
        self.service.model.generate_content.return_value = mock_response
        
        mock_models.FoodItem.objects.filter.return_value.first.return_value = None
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Apple')

    def test_json_extraction_messy(self):
        mock_response = MagicMock()
        mock_response.text = 'Here is the data: {"items": [{"name": "Banana", "confidence": 0.8, "estimated_per_100g": {"calories": 89}}]} Enjoy!'
        self.service.model.generate_content.return_value = mock_response
        
        mock_models.FoodItem.objects.filter.return_value.first.return_value = None
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Banana')

    def test_blacklist_filtering(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "items": [
                {"name": "Pizza", "confidence": 0.9, "estimated_per_100g": {"calories": 266}},
                {"name": "Plate", "confidence": 0.9, "estimated_per_100g": {"calories": 0}},
                {"name": "Fork", "confidence": 0.7, "estimated_per_100g": {"calories": 0}}
            ]
        })
        self.service.model.generate_content.return_value = mock_response
        mock_models.FoodItem.objects.filter.return_value.first.return_value = None
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Pizza')

    def test_db_matching_exact(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "items": [{"name": "Greek Salad", "confidence": 0.9, "estimated_per_100g": {"calories": 100}}]
        })
        self.service.model.generate_content.return_value = mock_response
        
        db_mock = MockFoodItem("Greek Salad", 150, 5, 10, 8)
        mock_models.FoodItem.objects.filter.return_value.first.return_value = db_mock
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(items[0]['calories'], 150) # From DB
        self.assertEqual(items[0]['name'], "Greek Salad")

    def test_low_confidence_filtering(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "items": [{"name": "Mystery", "confidence": 0.1, "estimated_per_100g": {"calories": 100}}]
        })
        self.service.model.generate_content.return_value = mock_response
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(len(items), 0)
        self.assertEqual(message, "No confident food detected")

    @patch('requests.get')
    def test_edamam_fallback(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.text = '{"items": [{"name": "Blueberry", "confidence": 1.0, "estimated_per_100g": {"calories": 10}}]}'
        self.service.model.generate_content.return_value = mock_response
        
        # No DB match
        mock_models.FoodItem.objects.filter.return_value.first.return_value = None
        
        # Edamam match
        mock_edamam_response = MagicMock()
        mock_edamam_response.json.return_value = {
            "hints": [{
                "food": {
                    "label": "Blueberry",
                    "nutrients": {"ENERC_KCAL": 57, "PROCNT": 0.7, "CHOCDF": 14, "FAT": 0.3}
                }
            }]
        }
        mock_requests_get.return_value = mock_edamam_response
        
        items, message = self.service.scan_food(io.BytesIO(b"fake_image"))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['calories'], 57) # From Edamam
        self.assertEqual(items[0]['name'], "Blueberry")

if __name__ == '__main__':
    unittest.main()
