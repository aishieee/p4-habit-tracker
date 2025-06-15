from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator




# Create your models here.
# Define the Habit model
class Habit(models.Model):
#Allow users to categorise habits
    CATEGORY_CHOICES = [
        ('health', 'Health/Fitness'),
        ('productivity', 'Productivity'),
        ('selfcare', 'Self-Care'),
        ('learning', 'Learning'),
        ('work', 'Work'),
        ('fun', 'Hobbies/Fun'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g. "Drink water"
    description = models.TextField(blank=True)
    target = models.PositiveIntegerField(default=1)  # e.g. "8 glasses/day"
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_template = models.BooleanField(default=False)  # For admin-curated templates
    
    # For admin-managed templates
    created_by_admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='admin_habits'
    )
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def is_completed_on(self, date):
        return self.completions.filter(date=date, completed=True).exists()

# Define the HabitCompletion model
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField(default=timezone.now)  # Date when habit was marked complete
    completed = models.BooleanField(default=True)  # Can be used for skip tracking
    notes = models.TextField(blank=True)  # Optional user notes
    
    class Meta:
        unique_together = ('habit', 'date')  # Prevent duplicate logs
    
    def __str__(self):
        return f"{self.habit.name} - {self.date}"

# Define the Streak model
class Streak(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='streaks')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Null means current streak
    count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.habit.name}: {self.count} days"

# Mark habit as done in dashboard
@property
def is_completed_today(self):
    return self.completions.filter(date=timezone.now().date()).exists()

# Allow user to create a note with optional pinning and timestamp
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

# Define badges in habit app 
class Badge(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='badges/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Track badge awarded to user 
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    

User = get_user_model()

def badge_upload_path(instance, filename):
    return f'badges/{instance.name}_{filename}'

class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    required_habits = models.ManyToManyField('Habit', related_name='challenges')  # new
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)

    def __str__(self):
        return self.name

class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def check_completion(self):
        required_habits = self.challenge.required_habits.all()
        completed_habit_ids = HabitCompletion.objects.filter(
            user=self.user,
            date__range=(self.challenge.start_date, self.challenge.end_date),
        ).values_list('habit_id', flat=True).distinct()

        # If ALL required habits are in the list of completed habits, mark challenge complete
        if all(habit.id in completed_habit_ids for habit in required_habits):
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            return True
        return False