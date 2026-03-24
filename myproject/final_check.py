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

def test_name():
    client = Client()
    # Login
    response = client.post('/api/login/', data=json.dumps({"email": "test@example.com", "password": "Password@123"}), content_type='application/json')
    token = response.json().get('token')
    
    # Create image
    img = Image.new('RGB', (10, 10), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Use name that should match Apple
    uploaded_image = SimpleUploadedFile("my_apple.png", img_byte_arr.getvalue(), content_type="image/png")
    
    response = client.post('/api/scan-food/', data={'image': uploaded_image, 'text': 'apple'}, HTTP_AUTHORIZATION=f'Token {token}')
    
    data = response.json().get('data', [])
    if data:
        print(f"DETECTED_NAME: {data[0].get('name')}")
    else:
        print("NO_DATA_DETECTED")

if __name__ == "__main__":
    test_name()
