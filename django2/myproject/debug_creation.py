import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.contrib.auth.models import User
from user.models import UserProfile
from django.db import IntegrityError, connection

def debug_creation():
    user_email = "debug_user@example.com"
    User.objects.filter(username=user_email).delete()
    
    print("1. Creating User...")
    user = User.objects.create_user(username=user_email, email=user_email, password="password123")
    
    print("2. Checking if Profile exists...")
    profile = UserProfile.objects.filter(user=user).first()
    if profile:
        print(f"Profile exists: ID={profile.id}, full_name={profile.full_name}, age={profile.age}")
    else:
        print("Profile does not exist. Creating manually...")
        profile = UserProfile(user=user)
    
    print("3. Setting fields...")
    profile.full_name = "Debug User"
    profile.status = "Active" # If this exists? No.
    profile.age = 20
    profile.gender = "Male"
    # Set ALL fields that were NO NULL in DESCRIBE
    profile.height_unit = "cm"
    profile.weight_unit = "kg"
    profile.health_conditions = []
    profile.food_allergies = []
    profile.allergies = []
    profile.dietary_restrictions = []
    profile.dislikes = []
    profile.goals = []
    
    print("4. Attempting Save...")
    try:
        profile.save()
        print("SUCCESS: Profile saved!")
    except IntegrityError as e:
        print(f"FAILED: IntegrityError: {e}")
        # Print SQL that would be run? No, let's just use connection.queries
        from django.db import connection
        print(f"Last Queries: {connection.queries[-2:]}")
    except Exception as e:
        print(f"FAILED: Unknown Error: {e}")

if __name__ == "__main__":
    debug_creation()
