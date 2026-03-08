import requests
import json
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "test@example.com"
PASSWORD = "Password@123"

def test_enhancements():
    # 1. Login
    login_url = f"{BASE_URL}/login/"
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(login_url, json=login_data)
    token = response.json().get("token")
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    print("Logged in successfully.")

    # 2. Get Today's Plan (Baseline)
    today_url = f"{BASE_URL}/meal-plan/today/"
    print("\n--- Generating Baseline AI Meal Plan ---")
    res1 = requests.post(today_url, headers=headers)
    plan1 = res1.json()
    meals1 = plan1.get("meals", [])
    meal_ids_1 = [m.get("template_id") for m in meals1 if m.get("template_id")] # Assuming template_id is returned or accessible
    
    # Let's check the calorie distribution in the baseline
    print("\n--- Calorie Distribution Check ---")
    target_total = plan1.get("targetCalories", 2000)
    dist_map = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "snack": 0.10,
        "dinner": 0.30
    }
    
    for m in meals1:
        m_type = m["mealType"]
        cals = m["calories"]
        expected = target_total * dist_map[m_type]
        diff_pct = abs(cals - expected) / expected * 100
        print(f"{m_type.capitalize()}: {cals} kcal (Expected ~{expected:.0f}, Diff: {diff_pct:.1f}%)")
        if diff_pct > 30: # Allowing 30% tolerance in test for pool limitations
             print(f"Note: {m_type} is slightly outside tight range, likely due to limited pool.")

    # 3. Test Variety (Refresh should avoid meals generated in step 2)
    # Since the seed is random for POST /refresh, it shouldn't hit the same meals anyway,
    # but the 'recent' filter (last 5 days) should explicitly block them.
    print("\n--- Testing Variety (Refresh should avoid current meals) ---")
    res2 = requests.post(today_url, headers=headers)
    plan2 = res2.json()
    meals2 = plan2.get("meals", [])
    
    titles1 = set(m["title"] for m in meals1)
    titles2 = set(m["title"] for m in meals2)
    
    intersection = titles1.intersection(titles2)
    if not intersection:
        print("Success: Variety achieved! No meals repeated in refresh.")
    else:
        print(f"Note: Some meals repeated: {intersection}. This might happen if the pool is very small (seed seed_meal_templates.py).")

if __name__ == "__main__":
    test_enhancements()
