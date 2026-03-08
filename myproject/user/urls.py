from django.urls import path
from .views import (
    RegisterView, LoginView, ForgotPasswordView, VerifyOTPView, ResetPasswordView, 
    PersonalDetailsView, BodyDetailsView, FoodPreferencesView, LifestyleActivityView, 
    GoalsView, GoalWeightView, HealthConditionsView, HealthDetailsView, MealsPerDayView, 
    HomeView, WaterTrackingView, TodayStepsView, WeeklyStepsView, ManualStepsLogView,
    FoodSearchView, LogFoodView, TodayMacrosView, FoodScanView,
    TodayMealPlanView, MealAlternativesView, SwapMealView, AiTipsView,
    FoodHistoryView, HistorySummaryView, SleepScheduleView, SleepLogView,
    RecipeListView, RecipeDetailView, FavoriteRecipeView, NutritionInsightsView,
    ProfileView, ChangePasswordView, ProfilePictureUploadView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('personal-details/', PersonalDetailsView.as_view(), name='personal-details'),
    path('body-details/', BodyDetailsView.as_view(), name='body-details'),
    path('food-preferences/', FoodPreferencesView.as_view(), name='food-preferences'),
    path('lifestyle-activity/', LifestyleActivityView.as_view(), name='lifestyle-activity'),
    path('goals/', GoalsView.as_view(), name='goals'),
    path('goal-weight/', GoalWeightView.as_view(), name='goal-weight'),
    path('health-conditions/', HealthConditionsView.as_view(), name='health-conditions'),
    path('health-details/', HealthDetailsView.as_view(), name='health-details'),
    path('meals-per-day/', MealsPerDayView.as_view(), name='meals-per-day'),

    # Professional Unified Profile Endpoints
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile-picture'),

    # Existing Home/Tracking views
    path('home/', HomeView.as_view(), name='home'),
    path('water-tracking/', WaterTrackingView.as_view(), name='water-tracking'),
    path('steps/today/', TodayStepsView.as_view(), name='steps-today'),
    path('steps/weekly/', WeeklyStepsView.as_view(), name='steps-weekly'),
    path('steps/manual-log/', ManualStepsLogView.as_view(), name='steps-manual-log'),
    path('foods/search/', FoodSearchView.as_view(), name='food-search'),
    path('log-food/', LogFoodView.as_view(), name='log-food'),
    path('today-macros/', TodayMacrosView.as_view(), name='today-macros'),
    path('food-scan/', FoodScanView.as_view(), name='food-scan'),
    
    # Recipe Endpoints
    path('recipes/', RecipeListView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipes/favorites/', FavoriteRecipeView.as_view(), name='favorite-recipe-list'),
    path('recipes/favorites/<int:recipe_id>/', FavoriteRecipeView.as_view(), name='favorite-recipe-detail'),
    
    # Meal Planning Endpoints
    path('meal-plan/today/', TodayMealPlanView.as_view(), name='today-meal-plan'),
    path('meal-plan/alternatives/', MealAlternativesView.as_view(), name='meal-alternatives'),
    path('meal-plan/swap/', SwapMealView.as_view(), name='swap-meal'),
    path('ai-tips/', AiTipsView.as_view(), name='ai-tips'),
    
    # History Endpoints
    path('food-history/', FoodHistoryView.as_view(), name='food-history'),
    path('history-summary/', HistorySummaryView.as_view(), name='history-summary'),
    
    # Sleep Tracking Endpoints
    path('sleep-schedule/', SleepScheduleView.as_view(), name='sleep-schedule'),
    path('sleep-logs/', SleepLogView.as_view(), name='sleep-logs'),
    
    # Nutrition Insights Endpoint
    path('nutrition-insights/', NutritionInsightsView.as_view(), name='nutrition-insights'),
]
