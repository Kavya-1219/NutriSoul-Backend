import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from user.models import UserProfile
from django.db import connection

def check_profile():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_userprofile WHERE id = 39")
        row = cursor.fetchone()
        print(f"Profile 39 Row Data: {row}")
        
    p = UserProfile.objects.filter(id=39).first()
    if p:
        print(f"p.full_name: {p.full_name}")
        print(f"p.age: {p.age}")
        print(f"p.gender: {p.gender}")

if __name__ == "__main__":
    check_profile()
