import requests
import json
import io
from PIL import Image

BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
SCAN_URL = f"{BASE_URL}/scan-food/"

def test_full_flow():
    # 1. Login
    login_data = {
        "email": "test@example.com",
        "password": "Password@123"
    }
    print(f"Logging in with {login_data['email']}...")
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response.raise_for_status()
        token = response.json().get('token')
        print(f"Login successful! Token: {token[:10]}...")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Scan Food
    headers = {
        "Authorization": f"Token {token}"
    }
    
    # Create a mock image
    img = Image.new('RGB', (100, 100), color = 'red') # Red for apple maybe?
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    files = {
        'image': ('test_apple.png', img_byte_arr, 'image/png')
    }
    data = {
        'text': 'This is an apple'
    }
    
    print(f"Testing {SCAN_URL}...")
    try:
        response = requests.post(SCAN_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
        print("Scan result:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Scan failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(e.response.text)

if __name__ == "__main__":
    # Ensure server is running or mock the request if needed?
    # Actually, I can't be sure the server is running on 8000. 
    # I'll try to run the Django server in the background first if possible.
    test_full_flow()
