import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_user():
    email = "test@example.com"
    username = "testuser"
    password = "Password@123"
    
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"User created: {email}")
    else:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        print(f"User updated: {email}")

if __name__ == "__main__":
    create_test_user()
