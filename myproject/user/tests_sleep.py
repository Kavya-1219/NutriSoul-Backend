
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from user.models import SleepSchedule, SleepLog
import datetime

class SleepTrackingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(username='usera', email='usera@example.com', password='password123!')
        self.user_b = User.objects.create_user(username='userb', email='userb@example.com', password='password123!')
        
    def test_unauthenticated_access_rejected(self):
        response = self.client.get('/api/sleep-schedule/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_sleep_schedule_defaults_on_first_get(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get('/api/sleep-schedule/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle potential variations in time formatting (HH:MM vs HH:MM:SS)
        self.assertTrue(response.data['bedtime'].startswith("22:00"))
        self.assertTrue(response.data['wake_time'].startswith("06:00"))
        self.assertFalse(response.data['reminder_enabled'])
        self.assertTrue(SleepSchedule.objects.filter(user=self.user_a).exists())

    def test_sleep_schedule_update(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
            "reminder_enabled": True
        }
        response = self.client.post('/api/sleep-schedule/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['bedtime'].startswith("23:00"))
        
        # Verify persistence
        schedule = SleepSchedule.objects.get(user=self.user_a)
        self.assertTrue(str(schedule.bedtime).startswith("23:00"))

    def test_sleep_log_upsert_and_isolation(self):
        self.client.force_authenticate(user=self.user_a)
        today = datetime.date.today()
        data = {
            "date": str(today),
            "bedtime": "22:00:00",
            "wake_time": "06:00:00",
            "duration": "8h 0m",
            "duration_minutes": 480,
            "quality": "Good"
        }
        
        # Create
        response = self.client.post('/api/sleep-logs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SleepLog.objects.filter(user=self.user_a).count(), 1)
        
        # Update (Upsert)
        data["quality"] = "Fair"
        response = self.client.post('/api/sleep-logs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SleepLog.objects.filter(user=self.user_a).count(), 1)
        self.assertEqual(SleepLog.objects.get(user=self.user_a, date=today).quality, "Fair")
        
        # Isolation: User B should see 0 logs
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get('/api/sleep-logs/')
        self.assertEqual(len(response.data['logs']), 0)
        self.assertEqual(response.data['weekly_average_hours'], 0.0)

    def test_weekly_average_and_limits(self):
        self.client.force_authenticate(user=self.user_a)
        base_date = datetime.date.today()
        
        # Create 8 logs (should only return 7)
        for i in range(8):
            SleepLog.objects.create(
                user=self.user_a,
                date=base_date - datetime.timedelta(days=i),
                bedtime="22:00:00",
                wake_time="06:00:00",
                duration="8h 0m",
                duration_minutes=480,
                quality="Good"
            )
            
        response = self.client.get('/api/sleep-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['logs']), 7)
        self.assertEqual(response.data['weekly_average_hours'], 8.0)
        
        # Check descending order
        dates = [log['date'] for log in response.data['logs']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_invalid_quality_rejected(self):
        self.client.force_authenticate(user=self.user_a)
        data = {
            "date": str(datetime.date.today()),
            "bedtime": "22:00:00",
            "wake_time": "06:00:00",
            "duration": "8h 0m",
            "duration_minutes": 480,
            "quality": "Excellent" # Invalid
        }
        response = self.client.post('/api/sleep-logs/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quality', response.data)
