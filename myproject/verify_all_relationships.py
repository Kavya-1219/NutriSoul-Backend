import os
import django
import json
from datetime import date, timedelta
from django.utils import timezone

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from user.models import UserProfile, DailyMealPlan, FoodLog, MealLog
from django.db import connection, IntegrityError

def verify():
    client = Client()
    # Use a brand new prefix to ensure no collision
    user_email = "verified_final_1122@example.com"
    print(f"Cleaning up user: {user_email}")
    User.objects.filter(username=user_email).delete()
    
    print("Step 0: Creating user...")
    user = User.objects.create_user(username=user_email, email=user_email, password="password123")
    print(f"User created: {user.id}")

    print("Step 1: Creating profile via SQL...")
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO user_userprofile 
            (user_id, full_name, age, gender, height_unit, weight_unit, cholesterol_level,
             todays_calories, todays_steps, todays_water_intake, dark_mode, 
             target_calories, target_weeks, bmr, activity_level, goal) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [user.id, 'Verified User', 25, 'Male', 'cm', 'kg', '', 
              0.0, 0, 0, 0, 2000, 12, 1500, 'Moderately Active', 'Maintain weight'])
    
    profile = UserProfile.objects.get(user=user)
    print(f"Profile created: {profile.id}")

    # 1. TEST SETTINGS -> MEAL PLAN RELATIONSHIP
    print("\n--- Testing Settings -> Meal Plan (Regeneration) ---")
    client.force_login(user)
    print("Step 2.1: Generating initial plan via API...")
    res_plan = client.get('/api/meal-plan/today/')
    assert res_plan.status_code == 200
    
    plan_query = DailyMealPlan.objects.filter(user=user, date=date.today())
    assert plan_query.exists()
    print(f"Initial Plan ID: {plan_query.first().id}")
    
    print("Step 2.2: Changing goal to 'Lose weight' (Triggering Invalidation)...")
    # We must use ORM to trigger the save() signal/method logic
    profile.goal = "Lose weight"
    profile.save() 
    
    plan_exists = DailyMealPlan.objects.filter(user=user, date=date.today()).exists()
    print(f"Plan exists after goal change? {plan_exists}")
    assert plan_exists is False, "DailyMealPlan should have been deleted on profile change"
    print("✓ Regeneration Trigger Verified")

    # 2. TEST LOG FOOD -> HOME/PROFILE RELATIONSHIP
    print("\n--- Testing Log Food -> Macro Sync ---")
    log_data = {
        "food_name": "Verified Chicken",
        "calories": 600,
        "protein": 60,
        "carbs": 0,
        "fats": 40,
        "quantity": 300,
        "meal_type": "Lunch",
        "date": str(date.today())
    }
    res_log = client.post('/api/log-food/', data=json.dumps(log_data), content_type='application/json')
    assert res_log.status_code == 201
    
    profile.refresh_from_db()
    print(f"Profile Today's Calories: {profile.todays_calories}")
    assert profile.todays_calories == 600
    
    res_home = client.get('/api/home/')
    home_data = res_home.json()
    print(f"Home View Today's Calories: {home_data['todays_calories']}")
    assert home_data['todays_calories'] == 600
    print("✓ Log Food -> Home/Profile Sync Verified")

    # 3. TEST LOG FOOD -> NUTRITION INSIGHTS RELATIONSHIP
    print("\n--- Testing Log Food -> Nutrition Insights ---")
    yesterday = timezone.now() - timedelta(days=1)
    FoodLog.objects.create(
        user=user, name="Yesterday Snack", 
        calories_per_unit=200, protein_per_unit=10, carbs_per_unit=20, fats_per_unit=5,
        quantity=1.0, # 200 calories
        timestamp=yesterday
    )
    
    res_insights = client.get('/api/nutrition-insights/')
    assert res_insights.status_code == 200
    insights = res_insights.json()
    print(f"Insights Days Logged: {insights['daysLogged']}")
    print(f"Insights Average Calories: {insights['averageCalories']}")
    
    # Total = 600 + 200 = 800. Average = 400.
    assert insights['daysLogged'] == 2
    assert abs(insights['averageCalories'] - 400) < 1.0
    print("✓ Insights Aggregation Verified")

    print("\nALL SCREEN RELATIONSHIPS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    verify()
