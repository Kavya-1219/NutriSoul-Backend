import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/recipes/"
LOGIN_URL = "http://127.0.0.1:8000/api/login/"
REGISTER_URL = "http://127.0.0.1:8000/api/register/"

TEST_EMAIL = "testuser_phase2@example.com"
TEST_PASSWORD = "testpassword123"

def get_token():
    # Try login
    response = requests.post(LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if response.status_code == 200:
        return response.json()['token']
    
    # Try register if login fails
    response = requests.post(REGISTER_URL, json={"username": "testuser_phase2", "email": TEST_EMAIL, "password": TEST_PASSWORD})
    if response.status_code == 201:
        # Login again to get token
        response = requests.post(LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        return response.json()['token']
    
    # Check if user already exists
    if response.status_code == 400:
        # User might exist, but check if we can get token anyway (maybe password was different in previous run)
        pass
    
    return None

def test_pagination():
    print("\n--- Testing Pagination ---")
    response = requests.get(BASE_URL)
    data = response.json()
    if "results" in data and "count" in data:
        print(f"✅ Pagination structure found. Count: {data['count']}")
    else:
        print("❌ Pagination structure MISSING")

def test_sorting():
    print("\n--- Testing Sorting ---")
    # Ascending
    response = requests.get(f"{BASE_URL}?sort=calories")
    data = response.json()['results']
    calories = [r['calories'] for r in data]
    if calories == sorted(calories):
         print("✅ Ascending sort (calories) works")
    else:
         print(f"❌ Ascending sort failed: {calories}")

    # Descending
    response = requests.get(f"{BASE_URL}?sort=-calories")
    data = response.json()['results']
    calories = [r['calories'] for r in data]
    if calories == sorted(calories, reverse=True):
         print("✅ Descending sort (-calories) works")
    else:
         print(f"❌ Descending sort failed: {calories}")

def test_nutrition_filters():
    print("\n--- Testing Nutrition Filters ---")
    # High Protein >= 15
    response = requests.get(f"{BASE_URL}?high_protein=true")
    data = response.json()['results']
    if all(r['protein'] >= 15 for r in data):
        print("✅ high_protein filter works")
    else:
        print(f"❌ high_protein filter failed: {[r['protein'] for r in data]}")

    # Low Calorie <= 200
    response = requests.get(f"{BASE_URL}?low_calories=true")
    data = response.json()['results']
    if all(r['calories'] <= 200 for r in data):
        print("✅ low_calories filter works")
    else:
        print(f"❌ low_calories filter failed: {[r['calories'] for r in data]}")

def test_favorites(token):
    if not token:
        print("Skipping Favorites test (no token)")
        return
    
    headers = {"Authorization": f"Token {token}"}
    print("\n--- Testing Favorites ---")
    
    # 1. Add favorite (ID: 1)
    response = requests.post(f"{BASE_URL}favorites/", json={"recipe_id": 1}, headers=headers)
    print(f"Add Favorite Status: {response.status_code}")
    if response.status_code in [201, 200]:
        print(f"✅ Add Favorite success: {response.json()['message']}")
    
    # 2. Add duplicate
    response = requests.post(f"{BASE_URL}favorites/", json={"recipe_id": 1}, headers=headers)
    if response.status_code == 200:
        print("✅ Duplicate handling works (returned 200)")

    # 3. List favorites
    response = requests.get(f"{BASE_URL}favorites/", headers=headers)
    data = response.json()
    if any(r['id'] == 1 for r in data):
        print("✅ Recipe 1 found in favorites list")
    
    # 4. Check is_favorite in list
    response = requests.get(BASE_URL, headers=headers)
    data = response.json()['results']
    recipe_1 = next((r for r in data if r['id'] == 1), None)
    if recipe_1 and recipe_1['is_favorite'] == True:
        print("✅ is_favorite is TRUE for favorite")
    else:
        print("❌ is_favorite is FALSE for favorite")

    # 5. Delete favorite
    response = requests.delete(f"{BASE_URL}favorites/1/", headers=headers)
    if response.status_code == 204:
        print("✅ Remove Favorite success")

    # 6. Check is_favorite after delete
    response = requests.get(BASE_URL, headers=headers)
    data = response.json()['results']
    recipe_1 = next((r for r in data if r['id'] == 1), None)
    if recipe_1 and recipe_1['is_favorite'] == False:
        print("✅ is_favorite is FALSE after removal")

def test_anonymous():
    print("\n--- Testing Anonymous Access ---")
    response = requests.get(BASE_URL)
    data = response.json()['results']
    if all(r['is_favorite'] == False for r in data):
        print("✅ Anonymous users get is_favorite=false")
    
    response = requests.post(f"{BASE_URL}favorites/", json={"recipe_id": 1})
    if response.status_code in [401, 403]:
        print("✅ Anonymous users blocked from favoriting")

if __name__ == "__main__":
    token = get_token()
    test_pagination()
    test_sorting()
    test_nutrition_filters()
    test_favorites(token)
    test_anonymous()
