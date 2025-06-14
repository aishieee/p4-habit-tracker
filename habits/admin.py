from django.contrib import admin
from .models import Habit, HabitCompletion, Streak
from .models import Badge, UserBadge

# Register your models here.
admin.site.register(Habit)
admin.site.register(HabitCompletion)
admin.site.register(Streak)

# View and manage all badges awarded to user

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    list_filter = ('badge', 'awarded_at')