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
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .forms import NoteForm
from .models import Note

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

@require_POST
@login_required
def toggle_habit(request, pk):
    """
    Toggle habit completion status
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.now().date()

    completion = HabitCompletion.objects.filter(habit=habit, date=today).first()
    if completion:
        completion.delete()
        completed = False
    else:
        HabitCompletion.objects.create(habit=habit, date=today, completed=True)
        completed = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'completed': completed})
    
    return redirect('habits:dashboard')

# Notes card 

@login_required
def add_note(request):
    """
    Allow users to create notes
    """
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('habits:note_list')
    else:
        form = NoteForm()
    return render(request, 'habits/add_note.html', {'form': form})

@login_required
def note_list(request):
    """
    List all the users notes, ordered by most recently saved
    """
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'habits/note_list.html', {'notes': notes})

@login_required
def edit_note(request, pk):
    """
    Allow user to edit an existing note 
    """
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        # Populate the form with submitted data and bind it to the existing note
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('habits:note_list')
    else:
        form = NoteForm(instance=note)

    return render(request, 'habits/edit_note.html', {'form': form})

@login_required
def delete_note(request, pk):
    """
    Allow user to confirm and delete a note
    """
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        note.delete()
        return redirect('habits:note_list')

    # Confirm before deleting
    return render(request, 'habits/delete_note.html', {'note': note})

# Calendar

def get_week_dates(start_date):
    """
    Show users a full week view on the calendar (Mon-Sun)
    """
    start = start_date - timedelta(days=start_date.weekday())
    return [start + timedelta(days=i) for i in range(7)]

def calendar_view(request):
    """
    Display the calendar for the current or selected week.
    """
    # Get the selected week from query parameters, or use today’s date if not provided
    week_str = request.GET.get("week")
    today = timezone.now().date()
    current_date = date.fromisoformat(week_str) if week_str else today

    # Generate a list of dates for the selected week (Mon–Sun)
    week_dates = get_week_dates(current_date)

    # Get all habits for the currently logged-in user
    habits = Habit.objects.filter(user=request.user)

    context = {
        "habits": habits,
        "week_dates": week_dates,
        "previous_week": current_date - timedelta(weeks=1),
        "next_week": current_date + timedelta(weeks=1),
    }

    return render(request, "habits/calendar.html", context)