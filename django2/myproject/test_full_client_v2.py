import os
import django
import sys
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
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
    
    # Use SimpleUploadedFile for Django Client
    uploaded_image = SimpleUploadedFile("test_apple.png", img_byte_arr.getvalue(), content_type="image/png")
    
    data = {
        'image': uploaded_image,
        'text': 'This is an apple'
    }
    
    # Use HTTP_AUTHORIZATION for Django test Client
    headers = {
        'HTTP_AUTHORIZATION': f'Token {token}'
    }
    
    print("Testing /api/scan-food/...")
    response = client.post('/api/scan-food/', data=data, **headers)
    
    print(f"Status: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Raw Response: {response.content}")

if __name__ == "__main__":
    test_full_flow_with_client()
