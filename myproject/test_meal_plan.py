import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "test@example.com"
PASSWORD = "Password@123"

def test_meal_plan():
    # 1. Login
    login_url = f"{BASE_URL}/login/"
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(login_url, json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json().get("token")
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    print("Logged in successfully.")

    # 2. Get Today's Plan
    today_url = f"{BASE_URL}/meal-plan/today/"
    print("\n--- Getting Today's Meal Plan ---")
    res1 = requests.get(today_url, headers=headers)
    print(f"Status: {res1.status_code}")
    plan1 = res1.json()
    print(json.dumps(plan1, indent=2))
    
    if len(plan1.get("meals", [])) != 4:
        print("Error: Expected 4 meals in the plan.")
    
    # 3. Verify Stability (GET again)
    print("\n--- Verifying Stability (GET again) ---")
    res2 = requests.get(today_url, headers=headers)
    plan2 = res2.json()
    if plan1 == plan2:
        print("Success: Stable seed works (same plan returned).")
    else:
        print("Warning: Stability check failed (different plan returned).")

    # 4. Refresh Plan
    print("\n--- Refreshing Today's Meal Plan ---")
    res3 = requests.post(today_url, headers=headers)
    plan3 = res3.json()
    if plan3 != plan2:
        print("Success: Refresh works (new plan returned).")
    else:
        print("Note: Refresh returned same plan (randomness choice or only one option).")

    # 5. Get Alternatives
    print("\n--- Getting Breakfast Alternatives ---")
    alt_url = f"{BASE_URL}/meal-plan/alternatives/?meal_type=breakfast"
    res4 = requests.get(alt_url, headers=headers)
    alts = res4.json()
    print(f"Found {len(alts)} alternatives for breakfast.")
    if alts:
        print(f"First selection: {alts[0]['title']} (ID: {alts[0]['id']})")
        
        # 6. Swap Meal
        print("\n--- Swapping Breakfast ---")
        swap_url = f"{BASE_URL}/meal-plan/swap/"
        swap_data = {"meal_type": "breakfast", "meal_template_id": alts[0]["id"]}
        res5 = requests.post(swap_url, json=swap_data, headers=headers)
        print(f"Swap Status: {res5.status_code}")
        if res5.status_code == 200:
            print(f"Swap body: {json.dumps(res5.json().get('plan', {}), indent=2)}")
            new_breakfast = next(m for m in res5.json()["plan"]["meals"] if m["mealType"] == "breakfast")
            if new_breakfast["title"] == alts[0]["title"]:
                print(f"Success: Meal swapped to {alts[0]['title']}")
            else:
                print("Error: Swapped meal title mismatch.")

        # 7. Test Swap Validation (Wrong Type)
        print("\n--- Testing Swap Validation (Wrong Type) ---")
        # Find a lunch item to swap for breakfast
        lunch_alt_url = f"{BASE_URL}/meal-plan/alternatives/?meal_type=lunch"
        lunch_alts = requests.get(lunch_alt_url, headers=headers).json()
        if lunch_alts:
            swap_data_wrong = {"meal_type": "breakfast", "meal_template_id": lunch_alts[0]["id"]}
            res6 = requests.post(swap_url, json=swap_data_wrong, headers=headers)
            print(f"Wrong Swap Status: {res6.status_code} (Expected 400)")
            print(f"Error Message: {res6.json().get('error')}")
            if res6.status_code == 400:
                print("Success: Incorrect meal type swap rejected.")
            else:
                print("Error: Incorrect meal type swap was NOT rejected.")

if __name__ == "__main__":
    test_meal_plan()
