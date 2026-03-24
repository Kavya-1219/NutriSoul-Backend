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

def final_verify():
    client = Client()
    # Use the new user we created
    u = User.objects.get(username='antigravity')
    t = Token.objects.get(user=u)
    token_key = t.key
    print(f"Using Token: {token_key}")
    
    # 1. Test with Biryani filename
    img = Image.new('RGB', (10, 10), color='yellow')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    file = SimpleUploadedFile("my_amazing_biryani.png", img_byte_arr.getvalue(), content_type="image/png")
    
    print("Testing identification for 'my_amazing_biryani.png'...")
    response = client.post('/api/scan-food/', {'image': file}, HTTP_AUTHORIZATION=f'Token {token_key}')
    
    data = response.json().get('data', [])
    if data:
        print(f"IDENTIFIED: {data[0].get('name')}")
    else:
        print(f"FAILED: {response.content}")

    # 2. Test with Burger text
    img_byte_arr.seek(0)
    file2 = SimpleUploadedFile("image.png", img_byte_arr.getvalue(), content_type="image/png") # generic name
    print("Testing identification for text='burger' and generic filename...")
    response = client.post('/api/scan-food/', {'image': file2, 'text': 'I am eating a burger'}, HTTP_AUTHORIZATION=f'Token {token_key}')
    
    data = response.json().get('data', [])
    if data:
        print(f"IDENTIFIED: {data[0].get('name')}")
    else:
        print(f"FAILED: {response.content}")

if __name__ == "__main__":
    final_verify()
