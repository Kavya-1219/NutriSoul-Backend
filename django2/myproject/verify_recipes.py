import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/recipes/"

def test_list():
    print("\n--- Testing Recipe List ---")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Count: {len(data)}")
        if data:
            print(f"Keys in first item: {list(data[0].keys())}")
            # Verify cookTime mapping
            if "cookTime" in data[0]:
                print("✅ cookTime mapping found")
            else:
                print("❌ cookTime mapping MISSING")
    else:
        print(f"Error: {response.text}")

def test_filter():
    print("\n--- Testing Category Filter (breakfast) ---")
    response = requests.get(f"{BASE_URL}?category=breakfast")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        categories = set(r['category'] for r in data)
        print(f"Categories found: {categories}")
        if all(c.lower() == 'breakfast' for c in categories):
            print("✅ Filter works correctly")
        else:
            print("❌ Filter failed")

def test_search():
    print("\n--- Testing Search (poha) ---")
    response = requests.get(f"{BASE_URL}?search=poha")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Items found: {[r['name'] for r in data]}")
        if any('poha' in r['name'].lower() for r in data):
            print("✅ Search works correctly")
        else:
            print("❌ Search failed")

def test_detail():
    print("\n--- Testing Detail (ID: 1) ---")
    response = requests.get(f"{BASE_URL}1/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Name: {data['name']}")
        print(f"Ingredients type: {type(data['ingredients'])}")
        print(f"Instructions type: {type(data['instructions'])}")
        if isinstance(data['ingredients'], list) and isinstance(data['instructions'], list):
            print("✅ Ingredients/Instructions are arrays")
        else:
            print("❌ Ingredients/Instructions are NOT arrays")
    else:
        print(f"Error: {response.text}")

def test_404():
    print("\n--- Testing 404 (ID: 9999) ---")
    response = requests.get(f"{BASE_URL}9999/")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Correctly returned 404")
    else:
        print(f"❌ Failed to return 404 (Status: {response.status_code})")

if __name__ == "__main__":
    try:
        test_list()
        test_filter()
        test_search()
        test_detail()
        test_404()
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Make sure the server is running at http://127.0.0.1:8000")
