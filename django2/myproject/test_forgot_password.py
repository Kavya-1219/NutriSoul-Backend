import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "final_1122@example.com" # Ensure this user exists or adjust accordingly

def test_forgot_password():
    print("--- Testing Forgot Password (OTP Generation) ---")
    data = {"email": EMAIL}
    response = requests.post(f"{BASE_URL}/forgot-password/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_verify_otp(otp):
    print("\n--- Testing Verify OTP ---")
    data = {"email": EMAIL, "otp": otp}
    response = requests.post(f"{BASE_URL}/verify-otp/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_reset_password(otp):
    print("\n--- Testing Reset Password ---")
    data = {
        "email": EMAIL,
        "otp": otp,
        "password": "NewPassword@123",
        "confirm_password": "NewPassword@123"
    }
    response = requests.post(f"{BASE_URL}/reset-password/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_forgot_password()
    print("\nCheck the server console for the generated OTP.")
    otp = input("Enter the OTP printed in the console: ")
    test_verify_otp(otp)
    test_reset_password(otp)
