import os
import django
import json
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import MealLog
from user.serializers import MealLogSerializer
from django.contrib.auth.models import User

user = User.objects.get(username='tester@example.com')
data = {
    "food_name": "Idli",
    "calories": 224,
    "protein": 5,
    "carbs": 50,
    "fats": 0.6,
    "quantity": 200,
    "meal_type": "Breakfast"
}

serializer = MealLogSerializer(data=data)
print(f"Is valid: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"Errors: {serializer.errors}")
else:
    try:
        serializer.save(user=user)
        print("Save successful")
    except Exception as e:
        import traceback
        traceback.print_exc()
