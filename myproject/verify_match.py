import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.services import FoodScanService
from user.models import FoodItem

def test_match():
    service = FoodScanService()
    
    # Check what's in DB
    all_foods = [f.name for f in FoodItem.objects.all()]
    print(f"Current foods in DB: {all_foods}")
    
    test_cases = ["cake", "Cake", "cakes", "Chocolate", "chocolate", "non", "vegetarian"]
    
    for tc in test_cases:
        match = service._find_food_match(tc)
        if match:
            print(f"MATCH FOUND: '{tc}' -> '{match.name}'")
        else:
            print(f"NO MATCH: '{tc}'")

if __name__ == "__main__":
    test_match()
