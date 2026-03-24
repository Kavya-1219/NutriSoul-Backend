import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import FoodItem

# List of foods requested by user
common_foods_data = [
    {"name": "Apple", "cals": 52, "pro": 0.3, "carb": 14, "fat": 0.2},
    {"name": "Banana", "cals": 89, "pro": 1.1, "carb": 23, "fat": 0.3},
    {"name": "Rice", "cals": 130, "pro": 2.7, "carb": 28, "fat": 0.3},
    {"name": "Dal", "cals": 116, "pro": 9, "carb": 21, "fat": 0.4},
    {"name": "Chapati", "cals": 297, "pro": 9, "carb": 46, "fat": 6},
    {"name": "Dosa", "cals": 168, "pro": 3.9, "carb": 29, "fat": 3.7},
    {"name": "Idli", "cals": 58, "pro": 1.6, "carb": 12, "fat": 0.1},
    {"name": "Paneer", "cals": 265, "pro": 18, "carb": 1.2, "fat": 20},
    {"name": "Egg", "cals": 155, "pro": 13, "carb": 1.1, "fat": 11},
    {"name": "Milk", "cals": 42, "pro": 3.4, "carb": 5, "fat": 1},
    {"name": "Salad", "cals": 15, "pro": 1, "carb": 3, "fat": 0.2},
    {"name": "Cucumber", "cals": 15, "pro": 0.7, "carb": 3.6, "fat": 0.1},
    {"name": "Tomato", "cals": 18, "pro": 0.9, "carb": 3.9, "fat": 0.2},
    {"name": "Burger", "cals": 295, "pro": 14, "carb": 24, "fat": 14},
    {"name": "Pizza", "cals": 266, "pro": 11, "carb": 33, "fat": 10},
    {"name": "Noodles", "cals": 138, "pro": 4.5, "carb": 25, "fat": 2.1},
    {"name": "Cake", "cals": 371, "pro": 5.3, "carb": 53, "fat": 15},
]

added = 0
for food in common_foods_data:
    obj, created = FoodItem.objects.get_or_create(
        name__iexact=food["name"],
        defaults={
            "name": food["name"],
            "calories_per_100g": food["cals"],
            "protein_per_100g": food["pro"],
            "carbs_per_100g": food["carb"],
            "fats_per_100g": food["fat"],
            "serving_unit": "g",
            "serving_quantity": 100
        }
    )
    if created:
        added += 1
        print(f"Added {food['name']}")

print(f"Seeding complete! Added {added} new foods.")
