import os
import django
import json
import io
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from user.models import FoodLog, UserProfile, MealLog

def verify_scan_to_dashboard():
    client = Client()
    
    # 1. Setup Test User
    user, _ = User.objects.get_or_create(username='scan_tester@example.com', email='scan_tester@example.com')
    user.set_password('password123')
    user.save()
    
    # Clear existing data for a clean test
    FoodLog.objects.filter(user=user).delete()
    MealLog.objects.filter(user=user).delete()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.todays_calories = 0
    profile.save()
    
    client.force_login(user)
    
    print("--- 1. Testing AI Food Scan ---")
    # Use a valid minimal 1x1 GIF to satisfy ImageField validation
    minimal_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
        b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
    )
    dummy_image = SimpleUploadedFile("food.gif", minimal_gif, content_type="image/gif")
    
    response = client.post('/api/food-scan/', {'image': dummy_image})
    print(f"Scan Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Scan Error Details: {response.content}")
    
    assert response.status_code == 200
    scan_results = response.json()
    print(f"Scan Results Preview: {list(scan_results.keys())}")
    
    # 2. Simulate User Picking a Result and Logging It
    print("\n--- 2. Testing Log Food (Scan Result) ---")
    # If scan returned items, pick the first one. Otherwise use a mock result.
    if scan_results["detected_items"] and scan_results["detected_items"][0]["name"] != "Uncertain result":
        item = scan_results["detected_items"][0]
        log_name = item["name"]
        log_calories = item["calories"]
        log_protein = item.get("protein", 0)
        log_carbs = item.get("carbs", 0)
        log_fats = item.get("fats", 0)
    else:
        print("No high-confidence items detected (likely due to dummy image/API key). Using mock detection result for logic verification.")
        log_name = "Chicken Curry"
        log_calories = 250
        log_protein = 20
        log_carbs = 10
        log_fats = 15

    log_payload = {
        "food_name": log_name,
        "calories": log_calories,
        "protein": log_protein,
        "carbs": log_carbs,
        "fats": log_fats,
        "quantity": 250, # 250g
        "meal_type": "Lunch",
        "date": str(date.today())
    }
    
    log_response = client.post('/api/log-food/', data=json.dumps(log_payload), content_type='application/json')
    print(f"Log Food Status: {log_response.status_code}")
    assert log_response.status_code == 201
    
    # 3. Verify Dashboard (HomeView)
    print("\n--- 3. Verifying Dashboard (HomeView) ---")
    home_response = client.get('/api/home/')
    print(f"Home Status: {home_response.status_code}")
    dashboard_data = home_response.json()
    
    print(f"Dashboard Calories: {dashboard_data.get('todays_calories')}")
    print(f"Profile Cached Calories: {UserProfile.objects.get(user=user).todays_calories}")
    
    # The LogFoodView should have created a FoodLog with multiplier 2.5
    # Total calories = log_calories (250) + any previous (0) = 250
    assert dashboard_data['todays_calories'] == log_calories
    assert UserProfile.objects.get(user=user).todays_calories == log_calories

    print("\nEnd-to-End Verification Successful!")
    print("Dashboard is correctly synchronized with scanning/logging actions.")

if __name__ == "__main__":
    verify_scan_to_dashboard()
