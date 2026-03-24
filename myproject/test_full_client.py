import os
import django
import sys
from django.test import Client
from PIL import Image
import io
import json

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def test_full_flow_with_client():
    client = Client()
    
    # 1. Login
    email = "test@example.com"
    password = "Password@123"
    
    print(f"Testing login for {email}...")
    response = client.post('/api/login/', data=json.dumps({"email": email, "password": password}), content_type='application/json')
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        return
        
    token = response.json().get('token')
    print(f"Login successful! Token: {token[:10]}...")
    
    # 2. Scan Food
    # Create a mock image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    data = {
        'image': img_byte_arr,
        'text': 'This is an apple'
    }
    
    headers = {
        'HTTP_AUTHORIZATION': f'Token {token}'
    }
    
    print("Testing /api/scan-food/...")
    # Django test client uses HTTP_ prefix for headers
    response = client.post('/api/scan-food/', data=data, **headers)
    
    print(f"Status: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_full_flow_with_client()
