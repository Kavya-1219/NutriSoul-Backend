import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.contrib.auth.models import User
from user.models import UserProfile

email = "test@example.com"
password = "Password@123"

user, created = User.objects.get_or_create(username=email, email=email)
user.set_password(password)
user.save()

profile, p_created = UserProfile.objects.get_or_create(user=user)
profile.full_name = "Test User"
profile.weight = 75
profile.height = 180
profile.age = 30
profile.gender = "Male"
profile.activity_level = "Moderately Active"
profile.goal = "Maintain weight"
profile.save()

print(f"User {email} {'created' if created else 'updated'} successfully with profile.")
