import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.db import connection

def final_raw_sql_test():
    with connection.cursor() as cursor:
        # Create a dummy user ID just for testing (if 1000 doesn't exist)
        try:
            print("Trying raw SQL INSERT...")
            cursor.execute("INSERT INTO user_userprofile (user_id, full_name, age, gender, height_unit, weight_unit, cholesterol_level, todays_calories, todays_steps, todays_water_intake, dark_mode, target_calories, target_weeks, bmr) VALUES (9999, 'Pure SQL User', 30, 'Male', 'cm', 'kg', '', 0.0, 0, 0, 0, 2000, 12, 1600)")
            print("SUCCESS!")
        except Exception as e:
            print(f"RAW SQL FAILED: {e}")

if __name__ == "__main__":
    final_raw_sql_test()
