from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import PersonalDetails, BodyDetails


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already registered."})

        validate_password(data["password"])
        return data

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        user = User.objects.create_user(
            username=email,   # important
            email=email,
            password=password
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = ["id", "full_name", "age", "gender", "created_at"]
        read_only_fields = ["id", "created_at"]


class BodyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyDetails
        fields = [
            "id",
            "height_value", "height_unit",
            "weight_value", "weight_unit",
            "bmi",
            "created_at",
        ]
        read_only_fields = ["id", "bmi", "created_at"]