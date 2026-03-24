from django.contrib import admin
from .models import (
    UserProfile, DailySteps, ManualStepsLog, FoodItem, MealLog,
    MealTemplate, MealTemplateItem, DailyMealPlan, DailyMealEntry,
    FoodLog, SleepSchedule, SleepLog, OTP
)

@admin.register(SleepSchedule)
class SleepScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'bedtime', 'wake_time', 'reminder_enabled', 'updated_at')
    search_fields = ('user__username',)

@admin.register(SleepLog)
class SleepLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'duration', 'quality', 'created_at')
    list_filter = ('quality', 'date')
    search_fields = ('user__username', 'date')

admin.site.register(FoodItem)
admin.site.register(MealLog)
admin.site.register(UserProfile)
admin.site.register(DailySteps)
admin.site.register(ManualStepsLog)
admin.site.register(OTP)
admin.site.register(FoodLog)
