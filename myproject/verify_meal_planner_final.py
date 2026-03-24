import requests
import json
from datetime import date

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "test@example.com"
PASSWORD = "Password@123"

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

def verify_all():
    # 1. Login
    print_section("AUTHENTICATION")
    login_url = f"{BASE_URL}/login/"
    login_data = {"email": EMAIL, "password": PASSWORD}
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            print(f"FAILED: Login error: {response.text}")
            return
        token = response.json().get("token")
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        print("SUCCESS: Logged in and received Auth Token.")
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return

    # 2. Daily Plan Generation (AI + BMI + Goal)
    print_section("MEAL PLAN GENERATION (AI + PERSONALIZATION)")
    today_url = f"{BASE_URL}/meal-plan/today/"
    # Using POST to force a fresh AI generation
    res_gen = requests.post(today_url, headers=headers)
    if res_gen.status_code != 200:
        print(f"FAILED: {res_gen.text}")
        return
    
    plan = res_gen.json()
    print(f"Target Calories: {plan.get('targetCalories')} kcal")
    print(f"Meals Generated: {len(plan.get('meals', []))}")
    
    for meal in plan.get("meals", []):
        print(f"- [{meal['mealType'].upper()}] {meal['title']} ({meal['calories']} kcal)")
        print(f"  Macros: P:{meal['protein']}g, C:{meal['carbs']}g, F:{meal['fats']}g")

    # 3. Variety Check (Recent Avoidance)
    print_section("VARIETY CHECK (REFRESH)")
    res_refresh = requests.post(today_url, headers=headers)
    new_plan = res_refresh.json()
    
    old_titles = [m['title'] for m in plan.get("meals", [])]
    new_titles = [m['title'] for m in new_plan.get("meals", [])]
    
    print("Previous Titles:", old_titles)
    print("New Titles:     ", new_titles)
    
    matches = set(old_titles).intersection(set(new_titles))
    if len(matches) == 0:
        print("SUCCESS: 100% variety! No meals repeated in the refresh.")
    else:
        print(f"VARIETY NOTE: {len(matches)} meals repeated. (Normal if pool is small).")

    # 4. Alternatives & Swapping
    print_section("ALTERNATIVES & SWAPPING")
    alt_url = f"{BASE_URL}/meal-plan/alternatives/?meal_type=breakfast"
    res_alt = requests.get(alt_url, headers=headers)
    alts = res_alt.json()
    
    if alts:
        print(f"Found {len(alts)} valid alternatives for Breakfast.")
        swap_template = alts[0]
        print(f"Attempting swap to: {swap_template['title']} (ID: {swap_template['id']})")
        
        swap_url = f"{BASE_URL}/meal-plan/swap/"
        swap_data = {"meal_type": "breakfast", "meal_template_id": swap_template["id"]}
        res_swap = requests.post(swap_url, json=swap_data, headers=headers)
        
        if res_swap.status_code == 200:
            print("SUCCESS: Meal swapped successfully on the server.")
        else:
            print(f"FAILED: Swap error: {res_swap.text}")
    else:
        print("FAILED: No alternatives found.")

    print_section("VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_all()
