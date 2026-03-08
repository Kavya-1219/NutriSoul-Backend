from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        # Special character validation as requested in UI: (!@#$%^&*)
        if not re.search(r"[!@#$%^&*]", value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*).")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Use email as username if username isn't provided (common for email-based login)
        validated_data.pop('confirm_password')
        email = validated_data.get('email')
        username = validated_data.get('username') or email
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                if not user.check_password(password):
                    raise serializers.ValidationError("Incorrect password.")
            else:
                raise serializers.ValidationError("No user found with this email.")
        else:
            raise serializers.ValidationError("Must include both email and password.")

        data['user'] = user
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        if not re.search(r"[!@#$%^&*]", value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*).")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='full_name')
    profilePictureUrl = serializers.SerializerMethodField()
    
    # CamelCase Mappings
    currentWeight = serializers.FloatField(source='current_weight')
    targetWeight = serializers.FloatField(source='target_weight')
    targetWeeks = serializers.IntegerField(source='target_weeks')
    mealsPerDay = serializers.IntegerField(source='meals_per_day')
    healthConditions = serializers.JSONField(source='health_conditions')
    foodAllergies = serializers.JSONField(source='food_allergies')
    dietaryRestrictions = serializers.JSONField(source='dietary_restrictions')
    targetCalories = serializers.IntegerField(source='target_calories')
    darkMode = serializers.BooleanField(source='dark_mode')
    
    # Legacy mappings
    systolic = serializers.IntegerField(source='systolic_bp')
    diastolic = serializers.IntegerField(source='diastolic_bp')
    thyroidCondition = serializers.CharField(source='thyroid_type')
    
    # Other CamelCase
    activityLevel = serializers.CharField(source='activity_level')
    diabetesType = serializers.CharField(source='diabetes_type')
    cholesterolLevel = serializers.CharField(source='cholesterol_level')
    otherAllergies = serializers.CharField(source='other_allergies')
    
    calorieGoal = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'email', 'name', 'age', 'gender', 'height', 'weight', 'bmi', 
            'diet_type', 'food_dislikes', 'activityLevel', 'goal', 'targetWeight',
            'currentWeight', 'targetWeeks', 'mealsPerDay', 'healthConditions', 
            'foodAllergies', 'allergies', 'dietaryRestrictions', 'dislikes',
            'systolic', 'diastolic', 'thyroidCondition', 'diabetesType', 
            'cholesterolLevel', 'otherAllergies', 'targetCalories', 'bmr',
            'darkMode', 'profilePictureUrl', 'calorieGoal',
            'todays_water_intake', 'todays_steps', 'todays_calories'
        )

    def get_profilePictureUrl(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_calorieGoal(self, obj):
        return obj.calculate_calorie_goal()

    def validate_age(self, value):
        if value <= 0 or value > 120:
             raise serializers.ValidationError("Please enter a valid age.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True, min_length=8)
    confirmPassword = serializers.CharField(required=True)

    def validate_newPassword(self, value):
        if not re.search(r"[!@#$%^&*]", value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*).")
        return value

    def validate(self, data):
        if data['newPassword'] != data['confirmPassword']:
            raise serializers.ValidationError({"confirmPassword": "Passwords do not match."})
        return data

from .models import DailySteps, ManualStepsLog

class DailyStepsSerializer(serializers.ModelSerializer):
    total_steps = serializers.ReadOnlyField()

    class Meta:
        model = DailySteps
        fields = ('date', 'auto_steps', 'manual_steps', 'goal_steps', 'total_steps', 'updated_at')

class ManualStepsLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualStepsLog
        fields = ('date', 'delta_steps', 'created_at')

from .models import FoodItem, MealLog

class FoodItemSerializer(serializers.ModelSerializer):
    calories = serializers.FloatField(source='calories_per_100g', read_only=True)
    protein = serializers.FloatField(source='protein_per_100g', read_only=True)
    carbs = serializers.FloatField(source='carbs_per_100g', read_only=True)
    fats = serializers.FloatField(source='fats_per_100g', read_only=True)
    servingQuantity = serializers.FloatField(source='serving_quantity', read_only=True)
    servingUnit = serializers.CharField(source='serving_unit', read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id',
            'name',
            'calories',
            'protein',
            'carbs',
            'fats',
            'servingQuantity',
            'servingUnit',
        ]

class MealLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealLog
        fields = [
            'id',
            'food_name',
            'calories',
            'protein',
            'carbs',
            'fats',
            'quantity',
            'meal_type',
            'date',
            'created_at',
        ]
        read_only_fields = ('id', 'created_at')

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        # Ensure numeric fields are positive
        for field in ['calories', 'protein', 'carbs', 'fats']:
            if data.get(field, 0) < 0:
                raise serializers.ValidationError({field: f"{field.capitalize()} cannot be negative."})
        return data

class FoodScanRequestSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    text = serializers.CharField(required=False, allow_blank=True, default="")
from .models import MealTemplate, MealTemplateItem, DailyMealPlan, DailyMealEntry

class MealTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealTemplateItem
        fields = ['name', 'quantity', 'calories', 'protein', 'carbs', 'fats']

class MealTemplateSerializer(serializers.ModelSerializer):
    items = MealTemplateItemSerializer(many=True, read_only=True)
    mealType = serializers.CharField(source='meal_type')
    
    class Meta:
        model = MealTemplate
        fields = ['id', 'mealType', 'title', 'calories', 'protein', 'carbs', 'fats', 'items']

class DailyMealEntrySerializer(serializers.ModelSerializer):
    mealType = serializers.CharField(source='meal_type')
    items = serializers.SerializerMethodField()

    class Meta:
        model = DailyMealEntry
        fields = ['mealType', 'title', 'calories', 'protein', 'carbs', 'fats', 'items']

    def get_items(self, obj):
        if obj.meal_template:
            return MealTemplateItemSerializer(obj.meal_template.items.all(), many=True).data
        return []

class DailyMealPlanSerializer(serializers.ModelSerializer):
    targetCalories = serializers.IntegerField(source='target_calories')
    meals = DailyMealEntrySerializer(many=True, read_only=True)

    class Meta:
        model = DailyMealPlan
        fields = ['targetCalories', 'meals']

class AiRecommendationSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    icon_bg = serializers.CharField()
    icon_tint = serializers.CharField()
    card_bg = serializers.CharField()
    border_color = serializers.CharField()
    category = serializers.CharField(required=False)

from .models import FoodLog

class FoodLogSerializer(serializers.ModelSerializer):
    timestamp_millis = serializers.SerializerMethodField()

    class Meta:
        model = FoodLog
        fields = [
            'id',
            'name',
            'calories_per_unit',
            'protein_per_unit',
            'carbs_per_unit',
            'fats_per_unit',
            'quantity',
            'unit',
            'timestamp_millis'
        ]

from .models import SleepSchedule, SleepLog

class SleepScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepSchedule
        fields = ['bedtime', 'wake_time', 'reminder_enabled']

class SleepLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepLog
        fields = ['date', 'bedtime', 'wake_time', 'duration', 'duration_minutes', 'quality']

    def validate_quality(self, value):
        valid_choices = [choice[0] for choice in SleepLog.QUALITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid quality. Must be one of {valid_choices}")
        return value

from .models import Recipe, FavoriteRecipe

class RecipeSerializer(serializers.ModelSerializer):
    cookTime = serializers.CharField(source='cook_time')
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'category', 'cookTime', 'calories', 'servings',
            'difficulty', 'ingredients', 'instructions', 'protein',
            'carbs', 'fats', 'fiber', 'image', 'is_favorite'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Ensure ingredients and instructions are always lists, never null
        if ret.get('ingredients') is None:
            ret['ingredients'] = []
        if ret.get('instructions') is None:
            ret['instructions'] = []
        return ret

class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ['id', 'user', 'recipe', 'created_at']
        read_only_fields = ['user', 'created_at']
