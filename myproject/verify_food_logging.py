import os
import django
import json
from datetime import date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from user.models import FoodItem, MealLog

def test_food_logging():
    client = Client()
    
    # 1. Create a test user
    user, created = User.objects.get_or_create(username='tester@example.com', email='tester@example.com')
    user.set_password('password123')
    user.save()
    
    # Clear existing logs for a fresh test
    MealLog.objects.filter(user=user).delete()
    
    # Get token if needed, but for internal test Client.force_login is easier
    client.force_login(user)
    
    print("--- Testing Food Search ---")
    response = client.get('/api/foods/search/?query=Idli')
    print(f"Search 'Idli' Status: {response.status_code}")
    print(f"Results: {response.json()}")
    assert response.status_code == 200
    assert any(item['name'] == 'Idli' for item in response.json())

    print("\n--- Testing Log Food ---")
    log_data = {
        "food_name": "Idli",
        "calories": 224,
        "protein": 5,
        "carbs": 50,
        "fats": 0.6,
        "quantity": 200,
        "meal_type": "Breakfast",
        "date": str(date.today())
    }
    response = client.post('/api/log-food/', data=json.dumps(log_data), content_type='application/json')
    print(f"Log Food Status: {response.status_code}")
    if response.status_code != 201:
        print(f"Error Response Body: {response.content}")
    assert response.status_code == 201
    
    # Log another item WITHOUT date (to test model default and refresh_from_db)
    log_data_no_date = {
        "food_name": "Paneer",
        "calories": 265,
        "protein": 18,
        "carbs": 1.2,
        "fats": 20,
        "quantity": 100,
        "meal_type": "Snack"
    }
    response_no_date = client.post('/api/log-food/', data=json.dumps(log_data_no_date), content_type='application/json')
    print(f"Log Food (No Date) Status: {response_no_date.status_code}")
    if response_no_date.status_code != 201:
        print(f"Error Response Body: {response_no_date.content}")
    assert response_no_date.status_code == 201

    print("\n--- Testing Today Macros ---")
    response = client.get('/api/today-macros/')
    print(f"Today Macros Status: {response.status_code}")
    totals = response.json()
    print(f"Totals: {totals}")
    assert response.status_code == 200
    
    expected_calories = 224 + 265
    expected_protein = 5 + 18
    
    print(f"Expected Type: {type(expected_calories)}")
    print(f"Actual Type: {type(totals['calories'])}")
    
    import math
    assert math.isclose(float(totals['calories']), expected_calories)
    assert math.isclose(float(totals['protein']), expected_protein)

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    try:
        test_food_logging()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
