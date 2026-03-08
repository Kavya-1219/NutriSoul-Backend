import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import FoodItem

foods = [
    {"name": "Idli", "calories_per_100g": 112, "protein_per_100g": 2.5, "carbs_per_100g": 25, "fats_per_100g": 0.3},
    {"name": "Dosa", "calories_per_100g": 133, "protein_per_100g": 3.4, "carbs_per_100g": 26, "fats_per_100g": 1.5},
    {"name": "Chapati", "calories_per_100g": 120, "protein_per_100g": 4, "carbs_per_100g": 22, "fats_per_100g": 1},
    {"name": "Rice", "calories_per_100g": 130, "protein_per_100g": 2.7, "carbs_per_100g": 28, "fats_per_100g": 0.3},
    {"name": "Dal", "calories_per_100g": 116, "protein_per_100g": 9, "carbs_per_100g": 20, "fats_per_100g": 0.4},
    {"name": "Egg", "calories_per_100g": 155, "protein_per_100g": 13, "carbs_per_100g": 1.1, "fats_per_100g": 11},
    {"name": "Milk", "calories_per_100g": 42, "protein_per_100g": 3.4, "carbs_per_100g": 5, "fats_per_100g": 1},
    {"name": "Banana", "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, "fats_per_100g": 0.3},
    {"name": "Apple", "calories_per_100g": 52, "protein_per_100g": 0.3, "carbs_per_100g": 14, "fats_per_100g": 0.2},
    {"name": "Paneer", "calories_per_100g": 265, "protein_per_100g": 18, "carbs_per_100g": 1.2, "fats_per_100g": 20},
    {"name": "Samosa", "calories_per_100g": 308, "protein_per_100g": 3.5, "carbs_per_100g": 32, "fats_per_100g": 18},
    {"name": "Vada", "calories_per_100g": 197, "protein_per_100g": 5, "carbs_per_100g": 24, "fats_per_100g": 9},
    {"name": "Pani Puri", "calories_per_100g": 150, "protein_per_100g": 2.5, "carbs_per_100g": 22, "fats_per_100g": 6},
    {"name": "Poha", "calories_per_100g": 180, "protein_per_100g": 3.3, "carbs_per_100g": 35, "fats_per_100g": 3},
    {"name": "Upma", "calories_per_100g": 132, "protein_per_100g": 3.5, "carbs_per_100g": 25, "fats_per_100g": 2},
    {"name": "Bonda", "calories_per_100g": 220, "protein_per_100g": 4, "carbs_per_100g": 28, "fats_per_100g": 10},
    {"name": "Tea", "calories_per_100g": 40, "protein_per_100g": 1, "carbs_per_100g": 4, "fats_per_100g": 2},
    {"name": "Coffee", "calories_per_100g": 45, "protein_per_100g": 1, "carbs_per_100g": 5, "fats_per_100g": 2},
    {"name": "Cake", "calories_per_100g": 257, "protein_per_100g": 3.4, "carbs_per_100g": 45, "fats_per_100g": 7.5},
    {"name": "Chocolate", "calories_per_100g": 546, "protein_per_100g": 4.9, "carbs_per_100g": 61, "fats_per_100g": 31},
    {"name": "Burger", "calories_per_100g": 295, "protein_per_100g": 13, "carbs_per_100g": 30, "fats_per_100g": 14},
    {"name": "Pizza", "calories_per_100g": 266, "protein_per_100g": 11, "carbs_per_100g": 33, "fats_per_100g": 10},
    {"name": "Noodles", "calories_per_100g": 138, "protein_per_100g": 4.5, "carbs_per_100g": 25, "fats_per_100g": 2.1},
    {"name": "Chips", "calories_per_100g": 536, "protein_per_100g": 7, "carbs_per_100g": 53, "fats_per_100g": 35},
    {"name": "Biscuit", "calories_per_100g": 450, "protein_per_100g": 6, "carbs_per_100g": 65, "fats_per_100g": 18},
]

for food in foods:
    FoodItem.objects.get_or_create(
        name=food["name"],
        defaults={
            "calories_per_100g": food["calories_per_100g"],
            "protein_per_100g": food["protein_per_100g"],
            "carbs_per_100g": food["carbs_per_100g"],
            "fats_per_100g": food["fats_per_100g"],
        }
    )

print("Sample foods seeded successfully.")
