from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from habits.models import HabitCompletion, Habit
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Send reminder emails to inactive users'

    def handle(self, *args, **kwargs):
        threshold_date = timezone.now().date() - timedelta(days=3)
        users = User.objects.all()

        for user in users:
            # Check if the user has any completions in the last 3 days
            recent_completions = HabitCompletion.objects.filter(
                habit__user=user,
                date__gte=threshold_date
            ).exists()

            if not recent_completions:
                send_mail(
                    subject='⏰ Habit Tracker Reminder',
                    message='Hey there! 👋\n\nYou haven’t tracked any habits for a few days.\nCome back and stay on track! 💪',
                    from_email='noreply@habittracker.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Reminder sent to {user.email}'))
