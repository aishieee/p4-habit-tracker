from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.utils import timezone 
from datetime import timedelta
from .models import Habit, HabitCompletion
from .forms import HabitForm, HabitCompletionForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import date
import json

# Create your views here.
def calculate_streak(habit):
    """
    Calculate the current streak of consecutive days a habit has been completed.
    """
    today = timezone.now().date()
    completions = habit.completions.filter(completed=True).order_by('-date')
    
    if not completions.exists():
        return 0  # No completions yet
    
    streak = 0
    current_date = today

    for completion in completions:
        if completion.date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break  # Streak is broken
    
    return streak

@login_required
def habit_create(request):
    """
    Handle the creation of a new habit.
    """
    if request.method == 'POST':
        form = HabitForm(request.POST, user=request.user)  # Pass user here
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit created successfully!')
            return redirect('habits:dashboard')
    else:
        form = HabitForm(user=request.user)  # Also pass user when loading the page
    
    return render(request, 'habits/add_habit.html', {'form': form})

@login_required
def habit_update(request, pk):
    """
    Handle updating an existing habit.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habit updated successfully!')
            return redirect('habits:dashboard')
    else:
        form = HabitForm(instance=habit)
    
    return render(request, 'habits/add_habit.html', {'form': form})

@login_required
def habit_delete(request, pk):
    """
    Handle deleting an existing habit.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('habits:dashboard')
    
    return render(request, 'habits/habit_confirm_delete.html', {'habit': habit})

@login_required
def log_completion(request, habit_id):
    """
    Log a habit completion for today.
    """
    habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
    today = timezone.now().date()
    
    # Check if a completion has already been logged today
    existing_completion = habit.completions.filter(date=today).first()

    if request.method == 'POST':
        form = HabitCompletionForm(request.POST, instance=existing_completion)
        if form.is_valid():
            completion = form.save(commit=False)
            completion.habit = habit
            completion.date = today
            completion.save()
            
            messages.success(request, f'Completion logged! Current streak: {calculate_streak(habit)} days')
            return redirect('habits:dashboard')
    else:
        form = HabitCompletionForm(instance=existing_completion)
    
    return render(request, 'habits/log_completion.html', {
        'form': form,
        'habit': habit,
        'existing_completion': existing_completion
    })

@login_required
def habit_detail(request, pk):
    """
    Display details of a habit including its completion history and streak.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    completions = habit.completions.order_by('-date')

    return render(request, 'habits/habit_detail.html', {
        'habit': habit,
        'completions': completions,
        'streak': calculate_streak(habit)
    })

def register(request):
    """
    Register form for user to create an account 
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after register
            return redirect('habits:dashboard')  # homepage
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """
    Display the user's dashboard overview.
    """
    habits = Habit.objects.filter(user=request.user)
    completions = HabitCompletion.objects.filter(habit__user=request.user)
    today = date.today()
    chart_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_data = [1, 2, 3, 2, 4, 1, 5]

    return render(request, 'habits/dashboard.html', {
        'habits': habits,
        'completions': completions,
        'today': today,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    })
