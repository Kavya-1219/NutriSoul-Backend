from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from user.models import FoodLog, UserProfile

def verify():
    client = APIClient()
    username = "test_insights_user"
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, email="test@example.com", password="password123!")
    
    # Setup Profile
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'full_name': 'Test User', 'age': 30, 'gender': 'Male'})
    profile.weight = 70
    profile.height = 175
    profile.activity_level = 'Moderately Active'
    profile.goal = 'Maintain weight'
    profile.save()
    
    client.force_authenticate(user=user)
    url = '/api/nutrition-insights/'

    # Case 1: Empty
    res1 = client.get(url)
    print(f"CASE 1 (Empty) - hasData: {res1.data['hasData']}")
    
    # Case 2: Data
    today = timezone.localtime(timezone.now())
    FoodLog.objects.create(
        user=user, name="Apple", calories_per_unit=50, protein_per_unit=0.3, carbs_per_unit=14, fats_per_unit=0.2,
        quantity=30.0, # 1500 cal
        timestamp=today
    )
    res2 = client.get(url)
    print(f"CASE 2 (Data) - avgCal: {res2.data['averageCalories']}, target: {res2.data['targetCalories']}")
    print(f"CASE 2 (Data) - status: {res2.data['calorieStatus']}")
    
    # CASE 3: Excellent Status (diff < 5%)
    print("Testing CASE 3: Excellent Status...")
    # Target 1500, Avg 1500
    # I'll manually set the profile's BMR logic? No, easier to just check if target 1500 works.
    # Actually, calculate_calorie_goal uses BMR. 
    # Let's just mock the response in the view if I could, but I'm testing the real view.
    # To get exactly 1500 target, I might need to fiddle with profile fields.
    # Or I can just trust the logic since I already tested 'Under Target'.
    # Let's try to get target close to 1500.
    # BMR for Male 30y, 175cm, 50kg: 88.362 + 13.397*50 + 4.799*175 - 5.677*30 = 88.362 + 669.85 + 839.825 - 170.31 = 1427.7
    # Sedentary multiplier 1.2 -> 1713.
    # If I set weight lower, I can get closer.
    profile.weight = 40
    profile.activity_level = 'Sedentary'
    profile.goal = 'Maintain weight'
    profile.save()
    res3 = client.get(url)
    print(f"CASE 3 (Excellent?) - avg: {res3.data['averageCalories']}, target: {res3.data['targetCalories']}")
    print(f"CASE 3 (Excellent?) - status: {res3.data['calorieStatus']['label']}")

    # Clean up
    User.objects.filter(username=username).delete()

verify()
