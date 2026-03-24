import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import FoodItem

def seed_foods():
    foods = [
        {"name": "Apple", "cal": 52, "prot": 0.3, "carb": 14, "fat": 0.2},
        {"name": "Banana", "cal": 89, "prot": 1.1, "carb": 23, "fat": 0.3},
        {"name": "Salad", "cal": 15, "prot": 1, "carb": 3, "fat": 0.2},
        {"name": "Cucumber", "cal": 15, "prot": 0.7, "carb": 3.6, "fat": 0.1},
        {"name": "Tomato", "cal": 18, "prot": 0.9, "carb": 3.9, "fat": 0.2},
        {"name": "Rice", "cal": 130, "prot": 2.7, "carb": 28, "fat": 0.3},
        {"name": "Dal", "cal": 116, "prot": 9, "carb": 20, "fat": 0.4},
        {"name": "Idli", "cal": 58, "prot": 2, "carb": 12, "fat": 0.1},
        {"name": "Dosa", "cal": 168, "prot": 3.9, "carb": 29, "fat": 3.7},
        {"name": "Chapati", "cal": 264, "prot": 9, "carb": 56, "fat": 3.5},
        {"name": "Paneer", "cal": 265, "prot": 18, "carb": 1.2, "fat": 20},
        {"name": "Egg", "cal": 155, "prot": 13, "carb": 1.1, "fat": 11},
        {"name": "Milk", "cal": 42, "prot": 3.4, "carb": 5, "fat": 1},
        {"name": "Burger", "cal": 295, "prot": 17, "carb": 24, "fat": 14},
        {"name": "Pizza", "cal": 266, "prot": 11, "carb": 33, "fat": 10},
        {"name": "Noodles", "cal": 138, "prot": 4.5, "carb": 25, "fat": 2.1},
        {"name": "Cake", "cal": 257, "prot": 3, "carb": 40, "fat": 10},
        {"name": "Chocolate", "cal": 546, "prot": 4.9, "carb": 61, "fat": 31},
        {"name": "Biscuit", "cal": 483, "prot": 7, "carb": 66, "fat": 21},
        {"name": "Chips", "cal": 536, "prot": 7, "carb": 53, "fat": 35},
    ]

    for f in foods:
        FoodItem.objects.update_or_create(
            name=f["name"],
            defaults={
                "calories_per_100g": f["cal"],
                "protein_per_100g": f["prot"],
                "carbs_per_100g": f["carb"],
                "fats_per_100g": f["fat"],
                "serving_quantity": 100.0,
                "serving_unit": "g"
            }
        )
    print(f"Successfully seeded {len(foods)} food items.")

if __name__ == "__main__":
    seed_foods()
