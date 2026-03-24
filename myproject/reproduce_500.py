import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from user.models import UserProfile
from user.serializers import UserProfileSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def debug_profile():
    user = User.objects.all().first()
    if not user:
        print("No user found")
        return

    print(f"Debugging profile for user: {user.email}")
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    factory = APIRequestFactory()
    request = factory.get('/api/profile/')
    
    # Wrap in a DRF Request object to provide context if needed
    drf_request = Request(request)
    
    try:
        serializer = UserProfileSerializer(profile, context={'request': drf_request})
        data = serializer.data
        print("Serialization successful")
        # print(data)
    except Exception as e:
        print(f"Serialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_profile()
