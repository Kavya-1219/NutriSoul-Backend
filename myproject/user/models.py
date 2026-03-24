from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import datetime
import logging

logger = logging.getLogger(__name__)

class OTP(models.Model):
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.code}"

    def is_expired(self):
        # OTP is valid for 5 minutes
        expiration_time = self.created_at + datetime.timedelta(minutes=5)
        return timezone.now() > expiration_time

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    DIET_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Non-Vegetarian', 'Non-Vegetarian'),
        ('Eggetarian', 'Eggetarian'),
        ('Vegan', 'Vegan'),
    ]

    ACTIVITY_CHOICES = [
        ('Sedentary', 'Sedentary'),
        ('Lightly Active', 'Lightly Active'),
        ('Moderately Active', 'Moderately Active'),
        ('Very Active', 'Very Active'),
    ]

    GOAL_CHOICES = [
        ('Lose weight', 'Lose weight'),
        ('Maintain weight', 'Maintain weight'),
        ('Gain weight', 'Gain weight'),
        ('Gain muscle', 'Gain muscle'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, default="")
    height = models.FloatField(default=0.0, null=True, blank=True)
    height_unit = models.CharField(max_length=5, default='cm')
    weight = models.FloatField(default=0.0, null=True, blank=True)
    weight_unit = models.CharField(max_length=5, default='kg')
    bmi = models.FloatField(null=True, blank=True)
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES, null=True, blank=True)
    
    # List fields using JSONField
    health_conditions = models.JSONField(default=list, blank=True)
    food_allergies = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    dietary_restrictions = models.JSONField(default=list, blank=True)
    dislikes = models.JSONField(default=list, blank=True)
    
    food_dislikes = models.TextField(null=True, blank=True) # Legacy
    activity_level = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, null=True, blank=True)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, null=True, blank=True) # Single goal for legacy components
    goals = models.JSONField(default=list, blank=True) # Multi-select support
    
    # Weight and Goals
    target_weight = models.FloatField(default=0.0, null=True, blank=True)
    current_weight = models.FloatField(default=0.0, null=True, blank=True)
    target_weeks = models.PositiveIntegerField(default=12)
    target_calories = models.PositiveIntegerField(default=0)
    bmr = models.PositiveIntegerField(default=0)
    
    def recalculate_metrics(self):
        """Recalculates BMI, BMR and Calorie Goal based on current body details."""
        if self.weight and self.height:
            self.bmi = self.calculate_bmi()
            self.bmr = int(self.calculate_bmr())
            self.target_calories = self.calculate_calorie_goal()
            
        # Keep current_weight in sync with weight for legacy UI components
        if self.weight and not self.current_weight:
            self.current_weight = self.weight
        elif self.current_weight and not self.weight:
            self.weight = self.current_weight

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_profile = None
        if not is_new:
            try:
                old_profile = UserProfile.objects.get(pk=self.pk)
            except UserProfile.DoesNotExist:
                pass

        self.recalculate_metrics()
        super().save(*args, **kwargs)

        # Trigger regeneration of Meal Plan if critical fields changed
        if old_profile:
            critical_fields = [
                'age', 'gender', 'height', 'weight', 'activity_level', 
                'goal', 'goals', 'diet_type', 'food_allergies', 
                'allergies', 'dislikes', 'food_dislikes', 
                'health_conditions', 'meals_per_day', 'target_weight',
                'systolic_bp', 'diastolic_bp', 'cholesterol_level',
                'thyroid_type', 'diabetes_type'
            ]
            changed = False
            for field in critical_fields:
                if getattr(self, field) != getattr(old_profile, field):
                    changed = True
                    break
            
            if changed:
                from .models import DailyMealPlan
                from datetime import date
                today = date.today()
                DailyMealPlan.objects.filter(user=self.user, date=today).delete()
                logger.info(f"Meal plan invalidated for user {self.user.email} due to profile change.")
    
    # Health Metrics (Legacy names kept in DB, mapped in Serializer)
    systolic_bp = models.IntegerField(null=True, blank=True)
    diastolic_bp = models.IntegerField(null=True, blank=True)
    thyroid_type = models.CharField(max_length=100, null=True, blank=True) # Acts as thyroidCondition
    diabetes_type = models.CharField(max_length=50, null=True, blank=True)
    cholesterol_level = models.CharField(max_length=50, blank=True, default="")
    other_allergies = models.TextField(null=True, blank=True)
    meals_per_day = models.PositiveIntegerField(default=3, null=True, blank=True)

    # Settings
    dark_mode = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Tracking fields
    todays_water_intake = models.PositiveIntegerField(default=0)
    todays_steps = models.PositiveIntegerField(default=0)
    todays_calories = models.FloatField(default=0.0)

    def calculate_bmr(self):
        if not self.weight or not self.height or not self.age:
            return 0
        if self.gender == 'Male':
            return 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            return 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)

    def calculate_calorie_goal(self):
        bmr = self.calculate_bmr()
        if bmr == 0:
            return 0
            
        activity_multipliers = {
            'Sedentary': 1.2,
            'Lightly Active': 1.375,
            'Moderately Active': 1.55,
            'Very Active': 1.725
        }
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        tdee = bmr * multiplier

        # Handle multi-select goals (prioritize goals list)
        goals_list = self.goals or []
        is_lose_weight = 'Lose weight' in goals_list or self.goal == 'Lose weight'
        is_gain_weight = 'Gain weight' in goals_list or 'Gain muscle' in goals_list or \
                         self.goal == 'Gain weight' or self.goal == 'Gain muscle'

        if is_lose_weight:
            return int(tdee - 500)
        elif is_gain_weight:
            return int(tdee + 500)
        return int(tdee)

    def calculate_bmi(self):
        if not self.weight or not self.height:
            return 0
        height_m = self.height / 100.0
        return self.weight / (height_m * height_m)

    def __str__(self):
        return f"{self.user.email} - {self.full_name}"

class DailySteps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_steps')
    date = models.DateField(default=timezone.now)
    auto_steps = models.PositiveIntegerField(default=0)
    manual_steps = models.PositiveIntegerField(default=0)
    goal_steps = models.PositiveIntegerField(default=10000)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    @property
    def total_steps(self):
        return self.auto_steps + self.manual_steps

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.total_steps} steps"

class ManualStepsLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manual_steps_logs')
    date = models.DateField(default=timezone.now)
    delta_steps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.delta_steps}"

class FoodItem(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    calories_per_100g = models.FloatField()
    protein_per_100g = models.FloatField()
    carbs_per_100g = models.FloatField()
    fats_per_100g = models.FloatField()
    serving_quantity = models.FloatField(default=100.0)
    serving_unit = models.CharField(max_length=50, default='g')

    def __str__(self):
        return self.name

class MealLog(models.Model):
    MEAL_TYPES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
        ('Snack', 'Snack'),
        ('Manual Entry', 'Manual Entry'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_logs')
    food_name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    quantity = models.FloatField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.food_name} - {self.meal_type}"
class MealTemplate(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    title = models.CharField(max_length=255)
    diet_type = models.CharField(max_length=50, null=True, blank=True) # e.g., 'vegetarian', 'nonveg'
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()

    def __str__(self):
        return f"{self.meal_type.capitalize()} - {self.title}"

class MealTemplateItem(models.Model):
    meal_template = models.ForeignKey(MealTemplate, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=100)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.quantity})"

class DailyMealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans')
    date = models.DateField(default=timezone.now)
    target_calories = models.IntegerField()

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date}"

class DailyMealEntry(models.Model):
    daily_meal_plan = models.ForeignKey(DailyMealPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=20)
    meal_template = models.ForeignKey(MealTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Snapshots for history
    title = models.CharField(max_length=255)
    calories = models.IntegerField()
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    is_eaten = models.BooleanField(default=False)
    is_consumed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meal_type.capitalize()} - {self.title}"

class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    name = models.CharField(max_length=255)
    
    # Store per 100g (mirroring Room entity)
    calories_per_unit = models.FloatField()
    protein_per_unit = models.FloatField()
    carbs_per_unit = models.FloatField()
    fats_per_unit = models.FloatField()
    
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, default='100g')
    
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
        ]

class SleepSchedule(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sleep_schedule')
    bedtime = models.TimeField(default="22:00")
    wake_time = models.TimeField(default="06:00")
    reminder_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Schedule"

class SleepLog(models.Model):
    QUALITY_CHOICES = [
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
        ('Over', 'Over'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_logs')
    date = models.DateField()
    bedtime = models.TimeField()
    wake_time = models.TimeField()
    duration = models.CharField(max_length=20)
    duration_minutes = models.PositiveIntegerField()
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_sleep_log_per_user_per_day')
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date} ({self.quality})"

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    cook_time = models.CharField(max_length=50)
    calories = models.IntegerField()
    servings = models.IntegerField()
    difficulty = models.CharField(max_length=50)
    ingredients = models.JSONField(default=list)
    instructions = models.JSONField(default=list)
    protein = models.IntegerField()
    carbs = models.IntegerField()
    fats = models.IntegerField()
    fiber = models.IntegerField()
    image = models.CharField(max_length=255) # Stores emoji or URL

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_user_recipe_favorite")
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"
