from django.contrib import admin
from .models import Habit, HabitCompletion, Streak

# Register your models here.
admin.site.register(Habit)
admin.site.register(HabitCompletion)
admin.site.register(Streak)