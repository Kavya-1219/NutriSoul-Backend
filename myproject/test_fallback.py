import os
import django
import io
from unittest.mock import MagicMock, patch

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.services import FoodScanService
from user.models import FoodItem

def test_fallback():
    # Ensure we have an Apple in DB
    apple, _ = FoodItem.objects.get_or_create(
        name="Apple",
        defaults={
            "calories_per_100g": 52,
            "protein_per_100g": 0.3,
            "carbs_per_100g": 14,
            "fats_per_100g": 0.2,
            "serving_quantity": 100,
            "serving_unit": "g"
        }
    )
    
    service = FoodScanService()
    
    # Create a dummy file with a specific name
    dummy_file = io.BytesIO(b"fake data")
    dummy_file.name = "fresh_red_apple_photo.jpg"
    
    print(f"Testing fallback for filename: {dummy_file.name}")
    
    # Simulate a quota error by patching generate_content
    with patch('PIL.Image.open') as mock_open:
        mock_open.return_value.convert.return_value = MagicMock()
        with patch.object(service.model, 'generate_content') as mock_gen:
            mock_gen.side_effect = Exception("Quota exceeded")
            
            items, message = service.scan_food(dummy_file, "")
            
            print(f"Message: {message}")
            print(f"Items: {items}")
            
            if items and items[0]['name'] == "Apple":
                print("VERIFICATION SUCCESS: Fallback correctly identified Apple")
            else:
                print("VERIFICATION FAILED: Fallback did not identify Apple")

if __name__ == "__main__":
    test_fallback()
