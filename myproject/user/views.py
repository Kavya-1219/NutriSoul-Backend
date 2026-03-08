from rest_framework import status, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from .serializers import (
    UserRegistrationSerializer, LoginSerializer, ForgotPasswordSerializer, 
    VerifyOTPSerializer, ResetPasswordSerializer, UserProfileSerializer,
    DailyStepsSerializer, ManualStepsLogSerializer, FoodItemSerializer, MealLogSerializer,
    FoodScanRequestSerializer, MealTemplateSerializer, DailyMealPlanSerializer,
    AiRecommendationSerializer, FoodLogSerializer, SleepScheduleSerializer, SleepLogSerializer,
    RecipeSerializer, ChangePasswordSerializer
)
from django.contrib.auth import authenticate, update_session_auth_hash
from .models import (
    OTP, UserProfile, DailySteps, ManualStepsLog, FoodItem, MealLog,
    MealTemplate, DailyMealPlan, FoodLog, SleepSchedule, SleepLog, Recipe, FavoriteRecipe
)
from django.db.models import Sum, Q
from datetime import timedelta
from .services import FoodScanService, MealPlanGenerator

class RecipePagination(pagination.PageNumberPagination):
    page_size = 10

class RecipeListView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        queryset = Recipe.objects.all()
        
        # 1. Category Filter
        category = request.query_params.get('category')
        if category and category.lower() != 'all':
            queryset = queryset.filter(category__iexact=category)
        
        # 2. Search
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        # 3. Nutrition Filters
        if request.query_params.get('high_protein') == 'true':
            queryset = queryset.filter(protein__gte=15)
        if request.query_params.get('low_carb') == 'true':
            queryset = queryset.filter(carbs__lte=20)
        if request.query_params.get('high_fiber') == 'true':
            queryset = queryset.filter(fiber__gte=7)
        if request.query_params.get('low_calories') == 'true':
            queryset = queryset.filter(calories__lte=200)

        # 4. Sorting
        sort = request.query_params.get('sort')
        if sort:
            # Only allow specific numeric fields for sorting
            # Format: 'calories' for asc, '-calories' for desc
            valid_sort_fields = [
                'calories', '-calories', 
                'protein', '-protein', 
                'carbs', '-carbs', 
                'fats', '-fats'
            ]
            if sort in valid_sort_fields:
                queryset = queryset.order_by(sort)

        # 5. Pagination
        paginator = RecipePagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = RecipeSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecipeDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
            serializer = RecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
            serializer = RecipeSerializer(recipe, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
            recipe.delete()
            return Response({"message": "Recipe deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

class FavoriteRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = FavoriteRecipe.objects.filter(user=request.user)
        recipes = [f.recipe for f in favorites]
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response({"error": "recipe_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipe = Recipe.objects.get(id=recipe_id)
            fav, created = FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                return Response({"message": "Recipe added to favorites"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Recipe is already in favorites"}, status=status.HTTP_200_OK)
        except Recipe.DoesNotExist:
            return Response({"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, recipe_id):
        try:
            favorite = FavoriteRecipe.objects.get(user=request.user, recipe_id=recipe_id)
            favorite.delete()
            return Response({"message": "Recipe removed from favorites"}, status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response({"error": "Favorite not found"}, status=status.HTTP_404_NOT_FOUND)

class TodayStepsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        steps, created = DailySteps.objects.get_or_create(
            user=request.user, 
            date=today,
            defaults={'goal_steps': 10000}
        )
        serializer = DailyStepsSerializer(steps)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        today = timezone.now().date()
        date_str = request.data.get('date')
        if date_str:
            try:
                target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = today

        steps, created = DailySteps.objects.get_or_create(user=request.user, date=target_date)
        
        # Update fields if provided
        auto_steps = request.data.get('auto_steps')
        manual_steps = request.data.get('manual_steps')
        goal_steps = request.data.get('goal_steps')

        if auto_steps is not None:
            steps.auto_steps = min(100000, max(0, int(auto_steps)))
        if manual_steps is not None:
            steps.manual_steps = min(100000, max(0, int(manual_steps)))
        if goal_steps is not None:
            steps.goal_steps = max(0, int(goal_steps))
        
        steps.save()

        # Update UserProfile for compatibility if it's today
        if target_date == today:
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile:
                profile.todays_steps = steps.total_steps
                profile.save()

        serializer = DailyStepsSerializer(steps)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WeeklyStepsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date_str = request.query_params.get('start')
        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to 6 days ago (total 7 days including today)
            start_date = timezone.now().date() - timedelta(days=6)

        end_date = start_date + timedelta(days=6)
        
        # Fetch existing records
        steps_records = DailySteps.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        records_dict = {steps.date: steps for steps in steps_records}
        
        # Prepare 7-day list
        days_data = []
        total_sum = 0.0
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            record = records_dict.get(current_date)
            
            if record:
                data = DailyStepsSerializer(record).data
            else:
                data = {
                    "date": current_date.isoformat(),
                    "auto_steps": 0,
                    "manual_steps": 0,
                    "total_steps": 0,
                    "goal_steps": 10000,
                    "updated_at": None
                }
            
            days_data.append(data)
            total_sum += float(data["total_steps"])

        avg_7_day = total_sum / 7
        
        return Response({
            "start": start_date.isoformat(),
            "days": days_data,
            "avg_7_day": float("{:.2f}".format(avg_7_day))
        }, status=status.HTTP_200_OK)

class ManualStepsLogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        delta = request.data.get('delta_steps')
        if delta is None:
            return Response({"error": "delta_steps is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        date_str = request.data.get('date')
        if date_str:
            try:
                target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()

        delta = int(delta)
        
        # Create log entry
        ManualStepsLog.objects.create(
            user=request.user,
            date=target_date,
            delta_steps=delta
        )
        
        # Update DailySteps
        steps, created = DailySteps.objects.get_or_create(user=request.user, date=target_date)
        current_manual = int(steps.manual_steps or 0)
        steps.manual_steps = min(100000, max(0, current_manual + delta))
        steps.save()

        # Update UserProfile for compatibility if it's today
        if target_date == timezone.now().date():
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile:
                profile.todays_steps = steps.total_steps
                profile.save()

        return Response({
            "message": "Manual steps logged successfully",
            "current_manual_steps": steps.manual_steps,
            "total_steps": steps.total_steps
        }, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = str(random.randint(100000, 999999))
            
            # Save OTP to database
            OTP.objects.create(email=email, code=otp_code)
            
            # Send OTP via email
            subject = 'Your Password Reset OTP'
            message = f'Your OTP for resetting your password is: {otp_code}. It is valid for 5 minutes.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            try:
                send_mail(subject, message, email_from, recipient_list)
                print(f"OTP for {email}: {otp_code}")
                return Response({
                    "message": "OTP sent successfully to your email."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error": f"Failed to send email: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            
            otp_obj = OTP.objects.filter(email=email, code=otp_code).last()
            
            if not otp_obj:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_obj.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            new_password = serializer.validated_data['password']
            
            otp_obj = OTP.objects.filter(email=email, code=otp_code).last()
            
            if not otp_obj or otp_obj.is_expired():
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Delete OTP after successful reset
            otp_obj.delete()
            
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.pk,
                "email": user.email,
                "username": user.username,
                "message": "Login successful"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PersonalDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if profile already exists for the user
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Personal details saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class BodyDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Body details saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class FoodPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Food preferences saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class LifestyleActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Lifestyle and activity details saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class GoalsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Goal saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class GoalWeightView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Target weight saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class HealthConditionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Health conditions saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class HealthDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Health details saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class MealsPerDayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Meal frequency saved successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(profile)
            data = serializer.data
            data['daily_tip'] = "You're doing great! Make sure to eat enough to meet your daily goals."
            return Response(data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile:
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        else:
            serializer = UserProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Home activity updated successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WaterTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            return Response({
                "todays_water_intake": profile.todays_water_intake,
                "daily_goal": 2275  # As seen in frontend WaterTrackingScreen.kt
            }, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        profile = UserProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # We can accept either an increment or a direct total
        increment = request.data.get('increment')
        if increment is not None:
            profile.todays_water_intake = max(0, profile.todays_water_intake + int(increment))
            profile.save()
            return Response({
                "message": "Water intake updated",
                "todays_water_intake": profile.todays_water_intake
            }, status=status.HTTP_200_OK)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Water intake updated",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FoodSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = (
            request.query_params.get('query')
            or request.query_params.get('q')
            or ''
        ).strip()
        if query:
            foods = FoodItem.objects.filter(name__icontains=query)[:20]
        else:
            # Return first 10 as recommended/suggested foods
            foods = FoodItem.objects.all()[:10]
        
        serializer = FoodItemSerializer(foods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogFoodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MealLogSerializer(data=request.data)
        if serializer.is_valid():
            meal_log = serializer.save(user=request.user)

            # Create FoodLog entry for history synchronization
            try:
                # Calculate per-100g values if needed, but LogFoodRequest already has absolute values
                # based on the quantity. However, HistoryViewModel expects per-100g values.
                # In LogFoodViewModel.kt, we see it saves per-100g values to FoodLogEntity.
                # Let's try to infer per-unit values.
                qty = meal_log.quantity or 1.0
                FoodLog.objects.create(
                    user=request.user,
                    name=meal_log.food_name,
                    calories_per_unit=meal_log.calories / (qty / 100.0) if qty > 0 else meal_log.calories,
                    protein_per_unit=meal_log.protein / (qty / 100.0) if qty > 0 else meal_log.protein,
                    carbs_per_unit=meal_log.carbs / (qty / 100.0) if qty > 0 else meal_log.carbs,
                    fats_per_unit=meal_log.fats / (qty / 100.0) if qty > 0 else meal_log.fats,
                    quantity=qty / 100.0,
                    unit="100g",
                    timestamp=meal_log.created_at or timezone.now()
                )
            except Exception as e:
                print(f"Error creating FoodLog entry: {e}")

            # Update UserProfile.todays_calories for legacy compatibility if it's today
            today = timezone.now().date()
            if meal_log.date == today:
                totals = MealLog.objects.filter(user=request.user, date=today).aggregate(
                    total_calories=Sum('calories'),
                    total_protein=Sum('protein'),
                    total_carbs=Sum('carbs'),
                    total_fats=Sum('fats')
                )

                profile = UserProfile.objects.filter(user=request.user).first()
                if profile:
                    profile.todays_calories = totals['total_calories'] or 0.0
                    profile.save(update_fields=['todays_calories'])

            meal_log.refresh_from_db()
            return Response(MealLogSerializer(meal_log).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodayMacrosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        logs = MealLog.objects.filter(user=request.user, date=today)
        
        totals = logs.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fats=Sum('fats')
        )
        
        return Response({
            "calories": totals['total_calories'] or 0.0,
            "protein": totals['total_protein'] or 0.0,
            "carbs": totals['total_carbs'] or 0.0,
            "fats": totals['total_fats'] or 0.0
        }, status=status.HTTP_200_OK)

class FoodScanView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FoodScanRequestSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            text = serializer.validated_data.get('text', '')
            
            service = FoodScanService()
            items, message = service.scan_food(image, text)
            
            return Response({
                "detected_items": items,
                "message": message
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodayMealPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        generator = MealPlanGenerator()
        # Stable seed: f"{user.id}-{today}"
        seed = f"{request.user.id}-{timezone.now().date()}"
        plan = generator.generate_daily_plan_for_user(request.user, seed)
        serializer = DailyMealPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Refresh today's plan
        generator = MealPlanGenerator()
        # Random seed for refresh
        seed = str(random.randint(0, 1000000))
        plan = generator.generate_daily_plan_for_user(request.user, seed, force_refresh=True)
        serializer = DailyMealPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MealAlternativesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meal_type = request.query_params.get('meal_type')
        if not meal_type:
            return Response({"error": "meal_type is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        generator = MealPlanGenerator()
        alternatives = generator.get_alternatives_for_user(request.user, meal_type)
        serializer = MealTemplateSerializer(alternatives, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SwapMealView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        meal_type = request.data.get('meal_type')
        meal_template_id = request.data.get('meal_template_id')

        if not meal_type or not meal_template_id:
            return Response({"error": "meal_type and meal_template_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        generator = MealPlanGenerator()
        plan, message = generator.swap_meal_for_user(request.user, meal_type, meal_template_id)

        if plan:
            serializer = DailyMealPlanSerializer(plan)
            return Response({
                "message": "Meal swapped successfully",
                "plan": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

class AiTipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        recommendations = []
        name = profile.full_name or "there"
        
        # 1. BMI Analysis
        if profile.height and profile.height > 0 and profile.weight and profile.weight > 0:
            bmi = profile.calculate_bmi()
            if bmi < 18.5:
                status_str = "Underweight"
                desc = "Your BMI is Underweight. Based on current trends, increasing calorie density is recommended to build healthy mass."
            elif bmi < 25:
                status_str = "Normal"
                desc = "Your BMI is Normal. You are in the optimal range. Focus on maintaining metabolic flexibility."
            elif bmi < 30:
                status_str = "Overweight"
                desc = "Your BMI is Overweight. A calorie deficit is recommended to reduce systemic inflammation."
            else:
                status_str = "Obese"
                desc = "Your BMI is Obese. A calorie deficit is recommended to reduce systemic inflammation."
            
            recommendations.append({
                "title": f"BMI Status: {bmi:.1f} ({status_str})",
                "description": desc,
                "icon": "info",
                "icon_bg": "#E1F5FE",
                "icon_tint": "#0288D1",
                "card_bg": "#F0F9FF",
                "border_color": "#BAE6FD",
                "category": "bmi"
            })

        # 2. Goal / Weight Gap
        if profile.weight and profile.target_weight:
            weight_diff = profile.target_weight - profile.weight
            goal = (profile.goal or "").lower()
            target_calories = profile.calculate_calorie_goal() or 1400

            if ( "lose" in goal or weight_diff < -0.5) and abs(weight_diff) > 0.5:
                # Losing weight
                recommendations.append({
                    "title": "Weight Management Strategy",
                    "description": f"To reach your target, you need to lose {abs(int(weight_diff))} kg. AI Suggestion: deficit around {target_calories} kcal with high protein to spare muscle.",
                    "icon": "trending_down",
                    "icon_bg": "#FEE2E2",
                    "icon_tint": "#DC2626",
                    "card_bg": "#FEF2F2",
                    "border_color": "#FECACA",
                    "category": "weight"
                })
                # Metabolic Support
                protein_g = int(target_calories * 0.25 / 4)
                # Metabolic Support
                protein_g = int(target_calories * 0.25 / 4)
                recommendations.append({
                    "title": "Metabolic Support",
                    "description": f"Target ~{protein_g}g of protein daily. This prevents metabolic slowdown while you're in a calorie deficit.",
                    "icon": "restaurant",
                    "icon_bg": "#E8F5E9",
                    "icon_tint": "#00C853",
                    "card_bg": "#F0FDF4",
                    "border_color": "#BBF7D0",
                    "category": "goal"
                })
            elif "muscle" in goal or "gain" in goal or weight_diff > 0.5:
                # Gaining weight/muscle
                recommendations.append({
                    "title": "Growth & Recovery Plan",
                    "description": f"Aiming for {max(0, int(weight_diff))} kg gain. AI Suggestion: consistent surplus (~{target_calories} kcal) paired with resistance training.",
                    "icon": "trending_up",
                    "icon_bg": "#FFF3E0",
                    "icon_tint": "#FF6D00",
                    "card_bg": "#FFFBEB",
                    "border_color": "#FDE68A",
                    "category": "goal"
                })
                # Anabolic Environment
                protein_g = max(60, int(profile.weight * 1.6))
                recommendations.append({
                    "title": "Anabolic Environment",
                    "description": f"Target ~1.6g/kg protein (~{protein_g}g/day) to maximize muscle protein synthesis. Spread across 4-5 meals.",
                    "icon": "fitness_center",
                    "icon_bg": "#F3E8FF",
                    "icon_tint": "#7C3AED",
                    "card_bg": "#FAF5FF",
                    "border_color": "#E9D5FF",
                    "category": "goal"
                })
            else:
                # Maintenance
                recommendations.append({
                    "title": "Maintenance & Optimization",
                    "description": f"Stay around {target_calories} kcal/day. Focus on dietary diversity and consistent sleep to optimize recovery.",
                    "icon": "track_changes",
                    "icon_bg": "#E8F5E9",
                    "icon_tint": "#00C853",
                    "card_bg": "#F0FDF4",
                    "border_color": "#BBF7D0",
                    "category": "goal"
                })

        # 3. Activity Optimization
        if profile.activity_level:
            activity = profile.activity_level.lower()
            goal_str = profile.goal or "health"
            if "sedentary" in activity:
                activity_desc = "Activity levels are low. Focus on NEAT (Non-Exercise Activity Thermogenesis) like standing or short walks."
            elif "light" in activity:
                activity_desc = "Daily activity is good. Adding 2 days of strength training will boost your BMR."
            elif "moderat" in activity:
                activity_desc = "Excellent activity level. Prioritize electrolyte balance and post-workout recovery."
            elif "active" in activity or "very" in activity:
                activity_desc = "High volume detected. Ensure you are meeting carbohydrate targets for glycogen replenishment."
            else:
                activity_desc = f"Consistent movement supports your overall health and {goal_str} goal."
            
            recommendations.append({
                "title": "Lifestyle Optimization",
                "description": activity_desc,
                "icon": "directions_run",
                "icon_bg": "#F1F8E9",
                "icon_tint": "#558B2F",
                "card_bg": "#F7FDF4",
                "border_color": "#DCEDC8",
                "category": "activity"
            })

        # 4. Vitals Analysis
        if profile.systolic_bp and profile.diastolic_bp:
            if profile.systolic_bp > 140 or profile.diastolic_bp > 90:
                recommendations.append({
                    "title": "Vitals Alert: BP Management",
                    "description": f"Recorded BP ({profile.systolic_bp}/{profile.diastolic_bp}) is elevated. AI Insight: Focus on the DASH diet (rich in potassium, calcium, and magnesium).",
                    "icon": "favorite",
                    "icon_bg": "#FFEBEE",
                    "icon_tint": "#D32F2F",
                    "card_bg": "#FFF1F2",
                    "border_color": "#FECACA",
                    "category": "vitals"
                })
        
        if profile.cholesterol_level:
            # Assumed logic: if it's an integer and high? In models.py it's IntegerField. 
            # In frontend it was string "high". Let's handle both or check range.
            # Assuming if > 200 it's high for this tip.
            if profile.cholesterol_level > 200:
                recommendations.append({
                    "title": "Cardiovascular Health",
                    "description": "Prioritize phytosterols and omega-3 fatty acids. Limit saturated fats to <7% of total calories.",
                    "icon": "monitor_heart",
                    "icon_bg": "#E0F2F1",
                    "icon_tint": "#00796B",
                    "card_bg": "#F0FDFD",
                    "border_color": "#B2DFDB",
                    "category": "vitals"
                })

        # 5. Condition Management
        if profile.health_conditions:
            # Frontend has a map of tips. Let's port them.
            health_tips = {
                "Diabetes": "Focus on high-fiber, low-GI foods. Prefer whole grains, legumes, veggies, and avoid sugary drinks.",
                "PCOS": "Include anti-inflammatory foods like nuts, seeds, fatty fish, and plenty of vegetables. Limit refined carbs.",
                "Thyroid Issues": "Ensure adequate iodine and selenium intake. Include eggs, dairy, nuts, and balanced meals.",
                "High Blood Pressure": "Limit sodium and include potassium-rich foods like bananas, spinach, coconut water, and dals.",
                "Low Blood Pressure": "Stay hydrated and consider small, frequent meals. Include electrolytes if needed.",
                "High Cholesterol": "Increase soluble fiber (oats, apples, beans) and healthy fats (olive oil, nuts).",
                "Digestive Issues": "Include probiotics/fermented foods and gradually increase fiber. Stay hydrated.",
                "Anemia": "Boost iron intake with vitamin C pairing (lemon, amla). Include leafy greens, legumes, and dates.",
                "Food Allergies": "Read labels carefully and avoid cross-contamination. Prefer simple, home-cooked meals."
            }
            # health_conditions is TextField, might be comma separated or JSON string
            conditions = [c.strip() for c in profile.health_conditions.split(',')]
            for condition in conditions:
                if condition in health_tips:
                    recommendations.append({
                        "title": f"Condition Management: {condition}",
                        "description": health_tips[condition],
                        "icon": "favorite_border",
                        "icon_bg": "#FFEBEE",
                        "icon_tint": "#D32F2F",
                        "card_bg": "#FFF1F2",
                        "border_color": "#FECACA",
                        "category": "condition"
                    })

        # 6. Hydration
        if profile.weight and profile.weight > 0:
            water_ml = max(1500, int(profile.weight * 35))
            glasses = max(6, int(water_ml / 250))
            recommendations.append({
                "title": "Fluid Balance",
                "description": f"Drink about {water_ml}ml daily (~{glasses} glasses). Hydration status directly impacts cognitive function and satiety.",
                "icon": "water_drop",
                "icon_bg": "#E3F2FD",
                "icon_tint": "#2962FF",
                "card_bg": "#EFF6FF",
                "border_color": "#BFDBFE",
                "category": "hydration"
            })

        # Final personalization: sort/cap
        # Ordering is already deterministic by the sequence above.
        final_list = recommendations[:7]
        
        serializer = AiRecommendationSerializer(final_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FoodHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.GET.get("days", 7))
        start_date = timezone.now() - timedelta(days=days)

        logs = FoodLog.objects.filter(
            user=request.user,
            timestamp__gte=start_date
        ).order_by('-timestamp')

        serializer = FoodLogSerializer(logs, many=True)
        return Response({
            "results": serializer.data
        }, status=status.HTTP_200_OK)

class HistorySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = FoodLog.objects.filter(user=request.user)

        # Count unique dates where food was logged
        days_logged = logs.values('timestamp__date').distinct().count()
        total_meals = logs.count()

        return Response({
            "days_logged": days_logged,
            "total_meals": total_meals
        }, status=status.HTTP_200_OK)

class SleepScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedule, created = SleepSchedule.objects.get_or_create(
            user=request.user,
            defaults={
                'bedtime': "22:00",
                'wake_time': "06:00",
                'reminder_enabled': False
            }
        )
        serializer = SleepScheduleSerializer(schedule)
        return Response(serializer.data)

    def post(self, request):
        schedule, created = SleepSchedule.objects.get_or_create(user=request.user)
        serializer = SleepScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SleepLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = SleepLog.objects.filter(user=request.user).order_by('-date')[:7]
        serializer = SleepLogSerializer(logs, many=True)
        
        # Calculate weekly average
        total_minutes = sum(log.duration_minutes for log in logs)
        avg_hours = 0.0
        if logs.exists():
            avg_minutes = total_minutes / logs.count()
            avg_hours = round(avg_minutes / 60.0, 1)

        return Response({
            "weekly_average_hours": avg_hours,
            "logs": serializer.data
        })

    def post(self, request):
        serializer = SleepLogSerializer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            defaults = {
                'bedtime': serializer.validated_data['bedtime'],
                'wake_time': serializer.validated_data['wake_time'],
                'duration': serializer.validated_data['duration'],
                'duration_minutes': serializer.validated_data['duration_minutes'],
                'quality': serializer.validated_data['quality'],
            }
            log, created = SleepLog.objects.update_or_create(
                user=request.user,
                date=date,
                defaults=defaults
            )
            return Response(SleepLogSerializer(log).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NutritionInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # 1. Date Range: Last 7 days, including today (using server/app timezone)
        today = timezone.localtime(timezone.now()).date()
        start_date = today - timedelta(days=6)
        
        # 2. Fetch logs in range
        logs = FoodLog.objects.filter(
            user=user,
            timestamp__date__range=[start_date, today]
        )
        
        # 3. Handle Empty State
        if not logs.exists():
            return Response(self._get_empty_response(), status=status.HTTP_200_OK)
            
        # 4. Group by local calendar date and aggregate
        daily_data = {}
        for log in logs:
            log_date = timezone.localtime(log.timestamp).date()
            if log_date not in daily_data:
                daily_data[log_date] = {
                    'calories': 0.0,
                    'protein': 0.0,
                    'carbs': 0.0,
                    'fats': 0.0
                }
            
            q = log.quantity
            daily_data[log_date]['calories'] += log.calories_per_unit * q
            daily_data[log_date]['protein'] += log.protein_per_unit * q
            daily_data[log_date]['carbs'] += log.carbs_per_unit * q
            daily_data[log_date]['fats'] += log.fats_per_unit * q
            
        days_logged = len(daily_data)
        
        # 5. Averaging Rule: Average over days that have logs only
        avg_calories = sum(d['calories'] for d in daily_data.values()) / days_logged
        avg_protein = sum(d['protein'] for d in daily_data.values()) / days_logged
        avg_carbs = sum(d['carbs'] for d in daily_data.values()) / days_logged
        avg_fats = sum(d['fats'] for d in daily_data.values()) / days_logged
        
        # 6. Target Calories from UserProfile
        target_calories = 2000
        profile = UserProfile.objects.filter(user=user).first()
        if profile:
            try:
                calc_target = profile.calculate_calorie_goal()
                if calc_target > 0:
                    target_calories = calc_target
            except Exception:
                pass
                
        # 7. Consistency
        weekly_consistency = days_logged / 7.0
        consistency_percent = int(round((days_logged / 7.0) * 100))
        
        # 8. Macro Percentages
        # Formula: (macro * multiplier / avg_calories) * 100
        # Multipliers: P=4, C=4, F=9
        if avg_calories > 0:
            protein_pct = int(round((avg_protein * 4.0 / avg_calories) * 100))
            carbs_pct = int(round((avg_carbs * 4.0 / avg_calories) * 100))
            fats_pct = int(round((avg_fats * 9.0 / avg_calories) * 100))
        else:
            protein_pct = carbs_pct = fats_pct = 0
            
        # 9. Calorie Status Logic
        status_info = self._get_calorie_status(int(round(avg_calories)), target_calories)
        
        # 10. Final Response (Numeric Formatting)
        return Response({
            "hasData": True,
            "weeklyConsistency": float(round(weekly_consistency, 2)),
            "consistencyPercent": consistency_percent,
            "daysLogged": days_logged,
            "totalDays": 7,
            "averageCalories": int(round(avg_calories)),
            "targetCalories": target_calories,
            "averageProtein": float(round(avg_protein, 1)),
            "averageCarbs": float(round(avg_carbs, 1)),
            "averageFats": float(round(avg_fats, 1)),
            "proteinPercentage": protein_pct,
            "carbsPercentage": carbs_pct,
            "fatsPercentage": fats_pct,
            "calorieStatus": status_info
        }, status=status.HTTP_200_OK)

    def _get_calorie_status(self, avg, target):
        if target <= 0:
            return {"label": "Unknown", "tone": "NEUTRAL", "emoji": "ℹ️"}
            
        diff = avg - target
        abs_diff_pct = abs(diff / float(target)) * 100.0
        
        if abs_diff_pct < 5.0:
            return {"label": "Excellent", "tone": "GOOD", "emoji": "🎯"}
        elif abs_diff_pct < 10.0:
            return {"label": "Good", "tone": "OK", "emoji": "👍"}
        elif diff > 0:
            return {"label": "Over Target", "tone": "WARN", "emoji": "⚠️"}
        else:
            return {"label": "Under Target", "tone": "INFO", "emoji": "📉"}

    def _get_empty_response(self):
        return {
            "hasData": False,
            "weeklyConsistency": 0.0,
            "consistencyPercent": 0,
            "daysLogged": 0,
            "totalDays": 7,
            "averageCalories": 0,
            "targetCalories": 2000,
            "averageProtein": 0.0,
            "averageCarbs": 0.0,
            "averageFats": 0.0,
            "proteinPercentage": 0,
            "carbsPercentage": 0,
            "fatsPercentage": 0,
            "calorieStatus": {
                "label": "Unknown",
                "tone": "NEUTRAL",
                "emoji": "ℹ️"
            }
        }

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['oldPassword']):
                return Response({"oldPassword": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['newPassword'])
            user.save()
            update_session_auth_hash(request, user)
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if 'profile_picture' in request.data:
            profile.profile_picture = request.data['profile_picture']
            profile.save()
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response({
                "message": "Profile picture updated successfully",
                "profilePictureUrl": serializer.data['profilePictureUrl']
            }, status=status.HTTP_200_OK)
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
