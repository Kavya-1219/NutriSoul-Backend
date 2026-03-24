import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/"
EMAIL = "test@example.com"
PASSWORD = "Password@123"

def test_ai_tips():
    # 1. Login
    print("--- Testing Login ---")
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(BASE_URL + "login/", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        # Try registering if login fails
        print("Attempting to register...")
        reg_data = {
            "email": EMAIL,
            "password": PASSWORD,
            "confirm_password": PASSWORD
        }
        response = requests.post(BASE_URL + "register/", json=reg_data)
        if response.status_code == 201:
             print("Registration successful.")
             response = requests.post(BASE_URL + "login/", json=login_data)
        else:
             print(f"Registration failed: {response.text}")
             return

    token = response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    print(f"Token acquired: {token[:10]}...")

    # 2. Update Profile with full data
    print("\n--- Updating Profile (Full Data) ---")
    profile_data = {
        "full_name": "Test User",
        "age": 30,
        "gender": "Male",
        "height": 180,
        "weight": 90,
        "activity_level": "Sedentary",
        "goal": "Lose weight",
        "target_weight": 80,
        "health_conditions": "Diabetes, High Blood Pressure",
        "systolic_bp": 150,
        "diastolic_bp": 95,
        "cholesterol_level": 220
    }
    requests.post(BASE_URL + "personal-details/", json=profile_data, headers=headers)
    requests.post(BASE_URL + "body-details/", json=profile_data, headers=headers)
    requests.post(BASE_URL + "health-details/", json=profile_data, headers=headers)
    requests.post(BASE_URL + "goals/", json=profile_data, headers=headers)

    # 3. Get AI Tips
    print("\n--- Getting AI Tips (Full Profile) ---")
    response = requests.get(BASE_URL + "ai-tips/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tips = response.json()
        print(f"Number of tips: {len(tips)}")
        for tip in tips:
            print(f"- {tip['category'].upper() if 'category' in tip else 'TIP'}: {tip['title']}")
            # print(f"  {tip['description']}")
    else:
        print(f"Failed to get tips: {response.text}")

    # 4. Update Profile with partial data
    print("\n--- Updating Profile (Partial Data) ---")
    profile_data_partial = {
        "height": 0,  # Missing/Invalid height
        "weight": 70,
        "health_conditions": "",
        "systolic_bp": None,
        "diastolic_bp": None
    }
    requests.post(BASE_URL + "body-details/", json=profile_data_partial, headers=headers)
    requests.post(BASE_URL + "health-details/", json=profile_data_partial, headers=headers)

    # 5. Get AI Tips (Partial)
    print("\n--- Getting AI Tips (Partial Profile) ---")
    response = requests.get(BASE_URL + "ai-tips/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tips = response.json()
        print(f"Number of tips: {len(tips)}")
        for tip in tips:
            print(f"- {tip.get('category', 'TIP').upper()}: {tip['title']}")
    else:
        print(f"Failed to get tips: {response.text}")

    # 6. Unauthenticated test
    print("\n--- Testing Unauthenticated Access ---")
    response = requests.get(BASE_URL + "ai-tips/")
    print(f"Status (should be 401/403): {response.status_code}")

if __name__ == "__main__":
    test_ai_tips()
