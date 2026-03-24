import requests

BASE_URL = "http://127.0.0.1:8000/api/"
EMAIL = "test@example.com"
PASSWORD = "Password@123"

def verify():
    print("--- Testing Login ---")
    response = requests.post(BASE_URL + "login/", json={"email": EMAIL, "password": PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return

    token = response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    print("\n--- Testing AI Tips ---")
    response = requests.get(BASE_URL + "ai-tips/", headers=headers)
    print(f"AiTips Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Tips count: {len(response.json())}")
    else:
        print(f"Error: {response.text}")

    print("\n--- Testing Home Data ---")
    response = requests.get(BASE_URL + "home/", headers=headers)
    print(f"Home Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Daily Tip: {data.get('dailyTip', 'MISSING')}")
        print(f"AI Tips count: {len(data.get('aiTips', []))}")
    else:
        print(f"Error: {data}")

if __name__ == "__main__":
    verify()
