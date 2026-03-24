import os
import django
from django.db.models import Sum
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user.models import MealLog, User
from django.db.models import Sum

user = User.objects.get(username='tester@example.com')
today = timezone.now().date()
logs = MealLog.objects.filter(user=user, date=today)

print(f"Number of logs: {logs.count()}")

totals = logs.aggregate(
    total_calories=Sum('calories'),
    total_protein=Sum('protein'),
    total_carbs=Sum('carbs'),
    total_fats=Sum('fats')
)

print(f"Totals from aggregate: {totals}")

response_data = {
    "calories": totals['total_calories'] or 0.0,
    "protein": totals['total_protein'] or 0.0,
    "carbs": totals['total_carbs'] or 0.0,
    "fats": totals['total_fats'] or 0.0
}

print(f"Final response data: {response_data}")
