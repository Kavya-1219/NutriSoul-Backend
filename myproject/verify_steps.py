import os
import django
import sys
from datetime import timedelta
from django.utils import timezone
# Setup Django environment
sys.path.append(r'c:\Users\vkavy\OneDrive\Desktop\frontend_backend\django2\myproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from user.models import DailySteps, ManualStepsLog, UserProfile

def run_verification():
    print("Starting verification of Steps Tracking API...")
    
    # Setup test user
    username = "testuser_steps"
    email = "test_steps@example.com"
    User.objects.filter(email=email).delete()
    user = User.objects.create_user(username=username, email=email, password="password123!")
    profile = UserProfile.objects.create(user=user, full_name="Test User", age=25, gender="Male")
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    today_str = timezone.now().date().isoformat()
    
    # 1. Test TodayStepsView GET
    print("\nTesting GET /steps/today/...")
    response = client.get('/api/steps/today/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['date'] == today_str
    print("GET today success.")
    
    # 2. Test TodayStepsView PUT (Upsert)
    print("\nTesting PUT /steps/today/...")
    payload = {
        "auto_steps": 5000,
        "manual_steps": 1000,
        "goal_steps": 12000
    }
    response = client.put('/api/steps/today/', payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['auto_steps'] == 5000
    assert response.data['manual_steps'] == 1000
    assert response.data['total_steps'] == 6000
    assert response.data['goal_steps'] == 12000
    
    # Verify profile update
    profile.refresh_from_db()
    assert profile.todays_steps == 6000
    print("PUT today success.")
    
    # 3. Test ManualStepsLogView POST
    print("\nTesting POST /steps/manual-log/...")
    payload = {
        "delta_steps": 500
    }
    response = client.post('/api/steps/manual-log/', payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['current_manual_steps'] == 1500
    assert response.data['total_steps'] == 6500
    
    # Test negative delta
    payload = {"delta_steps": -200}
    response = client.post('/api/steps/manual-log/', payload, format='json')
    assert response.data['current_manual_steps'] == 1300
    print("POST manual-log success.")
    
    # 4. Test WeeklyStepsView GET
    print("\nTesting GET /steps/weekly/...")
    response = client.get('/api/steps/weekly/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['days']) == 7
    assert response.data['days'][-1]['total_steps'] == 6300 # 6500 - 200
    print("GET weekly success.")
    
    print("\nVerification completed successfully!")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
