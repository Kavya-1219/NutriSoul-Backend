from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PersonalDetails(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="personal_details")
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - PersonalDetails"


class BodyDetails(models.Model):
    UNIT_HEIGHT = (("cm", "cm"), ("ft", "ft"))
    UNIT_WEIGHT = (("kg", "kg"), ("lbs", "lbs"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="body_details")

    height_value = models.FloatField(default=0)
    height_unit = models.CharField(max_length=5, choices=UNIT_HEIGHT, default="cm")

    weight_value = models.FloatField(default=0)
    weight_unit = models.CharField(max_length=5, choices=UNIT_WEIGHT, default="kg")

    bmi = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        height_cm = self.height_value
        if self.height_unit == "ft":
            height_cm = self.height_value * 30.48

        weight_kg = self.weight_value
        if self.weight_unit == "lbs":
            weight_kg = self.weight_value * 0.45359237

        if height_cm > 0:
            h_m = height_cm / 100
            self.bmi = round(weight_kg / (h_m * h_m), 1)
        else:
            self.bmi = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - BodyDetails {self.id}"


class PasswordResetOTP(models.Model):
    """
    Stores OTP for forgot password.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_otps")
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid 10 mins
        super().save(*args, **kwargs)

    def is_valid(self):
        return (not self.is_used) and (timezone.now() <= self.expires_at)

    def __str__(self):
        return f"{self.user.email} OTP {self.otp}"