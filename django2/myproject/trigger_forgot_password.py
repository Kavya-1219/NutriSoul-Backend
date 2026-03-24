import requests
import json

URL = "http://127.0.0.1:8000/api/forgot-password/"
DATA = {"email": "user@example.com"}

try:
    response = requests.post(URL, json=DATA)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
