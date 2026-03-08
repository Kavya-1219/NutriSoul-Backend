import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import MealTemplate, MealTemplateItem

def seed_meal_templates():
    # Data from MealPlanGenerator.kt
    pools = {
        "breakfast": [
            {
                "title": "Oats with Banana & Nuts", "calories": 380, "protein": 14, "carbs": 58, "fats": 10, "diet_type": "vegetarian",
                "items": [
                    {"name": "Oats", "quantity": "60g", "calories": 228, "protein": 7, "carbs": 39, "fats": 4},
                    {"name": "Banana", "quantity": "1 medium", "calories": 105, "protein": 1, "carbs": 27, "fats": 0},
                    {"name": "Milk", "quantity": "200ml", "calories": 47, "protein": 3, "carbs": 5, "fats": 2}
                ]
            },
            {
                "title": "Vegetable Poha", "calories": 420, "protein": 12, "carbs": 72, "fats": 10, "diet_type": "vegetarian",
                "items": [
                    {"name": "Poha", "quantity": "80g", "calories": 290, "protein": 6, "carbs": 60, "fats": 4},
                    {"name": "Veggies", "quantity": "100g", "calories": 50, "protein": 2, "carbs": 10, "fats": 0},
                    {"name": "Peanuts", "quantity": "10g", "calories": 80, "protein": 4, "carbs": 2, "fats": 6}
                ]
            },
            {
                "title": "Paneer Sandwich with Veggies", "calories": 323, "protein": 16, "carbs": 31, "fats": 16, "diet_type": "vegetarian",
                "items": [
                    {"name": "Whole Wheat Bread", "quantity": "2 slices", "calories": 140, "protein": 6, "carbs": 26, "fats": 2},
                    {"name": "Paneer", "quantity": "50g", "calories": 132, "protein": 9, "carbs": 2, "fats": 10},
                    {"name": "Vegetables (tomato, cucumber)", "quantity": "50g", "calories": 15, "protein": 1, "carbs": 3, "fats": 0},
                    {"name": "Butter", "quantity": "5g", "calories": 36, "protein": 0, "carbs": 0, "fats": 4}
                ]
            }
        ],
        "lunch": [
            {
                "title": "Dal + Brown Rice + Salad", "calories": 540, "protein": 22, "carbs": 86, "fats": 10, "diet_type": "vegetarian",
                "items": [
                    {"name": "Dal", "quantity": "200g", "calories": 240, "protein": 16, "carbs": 34, "fats": 6},
                    {"name": "Brown Rice", "quantity": "180g cooked", "calories": 210, "protein": 5, "carbs": 44, "fats": 2},
                    {"name": "Salad", "quantity": "150g", "calories": 90, "protein": 1, "carbs": 8, "fats": 2}
                ]
            },
            {
                "title": "Quinoa Paneer Bowl", "calories": 560, "protein": 28, "carbs": 62, "fats": 20, "diet_type": "vegetarian",
                "items": [
                    {"name": "Quinoa", "quantity": "180g cooked", "calories": 220, "protein": 8, "carbs": 39, "fats": 4},
                    {"name": "Paneer", "quantity": "80g", "calories": 210, "protein": 14, "carbs": 4, "fats": 16},
                    {"name": "Veggies", "quantity": "150g", "calories": 130, "protein": 6, "carbs": 19, "fats": 0}
                ]
            },
            {
                "title": "Paneer Curry with Quinoa", "calories": 457, "protein": 25, "carbs": 42, "fats": 21, "diet_type": "vegetarian",
                "items": [
                    {"name": "Quinoa", "quantity": "150g cooked", "calories": 167, "protein": 6, "carbs": 29, "fats": 3},
                    {"name": "Paneer Curry", "quantity": "150g", "calories": 265, "protein": 18, "carbs": 8, "fats": 18},
                    {"name": "Salad", "quantity": "100g", "calories": 25, "protein": 1, "carbs": 5, "fats": 0}
                ]
            }
        ],
        "dinner": [
            {
                "title": "Roti + Palak Paneer", "calories": 520, "protein": 26, "carbs": 58, "fats": 18, "diet_type": "vegetarian",
                "items": [
                    {"name": "Roti", "quantity": "2 medium", "calories": 142, "protein": 6, "carbs": 30, "fats": 1},
                    {"name": "Palak Paneer", "quantity": "200g", "calories": 318, "protein": 18, "carbs": 22, "fats": 17},
                    {"name": "Curd", "quantity": "100g", "calories": 60, "protein": 4, "carbs": 6, "fats": 2}
                ]
            },
            {
                "title": "Veg Khichdi + Curd", "calories": 480, "protein": 18, "carbs": 72, "fats": 12, "diet_type": "vegetarian",
                "items": [
                    {"name": "Khichdi", "quantity": "300g", "calories": 380, "protein": 14, "carbs": 62, "fats": 10},
                    {"name": "Curd", "quantity": "150g", "calories": 100, "protein": 4, "carbs": 10, "fats": 2}
                ]
            },
            {
                "title": "Roti with Palak Paneer", "calories": 382, "protein": 22, "carbs": 43, "fats": 16, "diet_type": "vegetarian",
                "items": [
                    {"name": "Roti", "quantity": "2 medium", "calories": 142, "protein": 6, "carbs": 30, "fats": 1},
                    {"name": "Palak Paneer", "quantity": "150g", "calories": 180, "protein": 12, "carbs": 8, "fats": 12},
                    {"name": "Curd", "quantity": "100g", "calories": 60, "protein": 4, "carbs": 6, "fats": 2}
                ]
            }
        ],
        "snack": [
            {
                "title": "Sprouts Salad", "calories": 180, "protein": 14, "carbs": 22, "fats": 4, "diet_type": "vegetarian",
                "items": [
                    {"name": "Mixed Sprouts", "quantity": "150g", "calories": 135, "protein": 12, "carbs": 22, "fats": 2},
                    {"name": "Lemon & Spices", "quantity": "10g", "calories": 10, "protein": 0, "carbs": 2, "fats": 0},
                    {"name": "Cucumber", "quantity": "100g", "calories": 35, "protein": 2, "carbs": 8, "fats": 0}
                ]
            },
            {
                "title": "Greek Yogurt Bowl", "calories": 200, "protein": 16, "carbs": 22, "fats": 5, "diet_type": "vegetarian",
                "items": [
                    {"name": "Greek Yogurt", "quantity": "200g", "calories": 150, "protein": 15, "carbs": 12, "fats": 4},
                    {"name": "Berries", "quantity": "80g", "calories": 50, "protein": 1, "carbs": 10, "fats": 1}
                ]
            },
            {
                "title": "Sprouts Salad (Light)", "calories": 95, "protein": 8, "carbs": 16, "fats": 1, "diet_type": "vegetarian",
                "items": [
                    {"name": "Mixed Sprouts", "quantity": "100g", "calories": 90, "protein": 8, "carbs": 15, "fats": 1},
                    {"name": "Lemon & Spices", "quantity": "10g", "calories": 5, "protein": 0, "carbs": 1, "fats": 0}
                ]
            }
        ]
    }

    for meal_type, meals in pools.items():
        for m_data in meals:
            template, created = MealTemplate.objects.get_or_create(
                title=m_data["title"],
                meal_type=meal_type,
                defaults={
                    "calories": m_data["calories"],
                    "protein": m_data["protein"],
                    "carbs": m_data["carbs"],
                    "fats": m_data["fats"],
                    "diet_type": m_data["diet_type"]
                }
            )
            
            if created:
                for i_data in m_data["items"]:
                    MealTemplateItem.objects.create(
                        meal_template=template,
                        name=i_data["name"],
                        quantity=i_data["quantity"],
                        calories=i_data["calories"],
                        protein=i_data["protein"],
                        carbs=i_data["carbs"],
                        fats=i_data["fats"]
                    )
                print(f"Created template: {template.title}")
            else:
                print(f"Template already exists: {template.title}")

if __name__ == "__main__":
    seed_meal_templates()
