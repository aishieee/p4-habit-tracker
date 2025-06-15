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
from .models import Habit
from datetime import datetime, timedelta, date
from datetime import date, timedelta
from django.db.models import Count
from .models import Badge, UserBadge
from django.utils.timezone import now

from django.shortcuts import get_object_or_404, redirect
from .models import Challenge, UserChallenge  # adjust if in a separate app
from django.http import HttpResponse
from .models import Challenge, HabitCompletion, UserChallenge

# Create your views here.

# Badges



def debug_check_challenge(request, challenge_id):
    user = request.user
    challenge = Challenge.objects.get(id=challenge_id)
    required_habits = challenge.required_habits.all()
    start = challenge.start_date
    end = challenge.end_date
    delta = (end - start).days + 1

    print(f"Checking challenge: {challenge.name}")
    print(f"Required habits: {[h.name for h in required_habits]}")
    print(f"From {start} to {end}")

    for habit in required_habits:
        for i in range(delta):
            check_date = start + timedelta(days=i)
            done = HabitCompletion.objects.filter(
                habit=habit,
                date=check_date,
                habit__user=user
            ).exists()
            print(f"{habit.name} on {check_date}: {'✅' if done else '❌'}")
            if not done:
                return HttpResponse("❌ Not completed")
    
    return HttpResponse("✅ Challenge Completed")


def check_challenge_completion(user):
    user_challenges = UserChallenge.objects.filter(user=user, completed=False)

    for uc in user_challenges:
        challenge = uc.challenge
        required_habits = challenge.required_habits.all()

        start = challenge.start_date
        end = challenge.end_date
        delta = (end - start).days + 1  # Inclusive

        completed = True

        for habit in required_habits:
            for i in range(delta):
                check_date = start + timedelta(days=i)
                if not HabitCompletion.objects.filter(user=user, habit=habit, date=check_date).exists():
                    completed = False
                    break
            if not completed:
                break

        if completed:
            uc.completed = True
            uc.save()

@login_required
def join_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)

    # Only create a UserChallenge if it doesn't exist
    UserChallenge.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )

    messages.success(request, "You have joined the challenge!")
    return redirect('habits:badges')  # or challenge detail

@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    user_habits = Habit.objects.filter(user=request.user)
    required = challenge.required_habits.all()

    missing = required.exclude(id__in=user_habits.values_list('id', flat=True))

    context = {
        'challenge': challenge,
        'missing_habits': missing,
    }
    return render(request, 'habits/challenge_detail.html', context)

def award_badge(user, slug):
    """
    Allow badges to be saved to database (Django admin - Userbadge table)
    """
    try:
        badge = Badge.objects.get(slug=slug)
        if not UserBadge.objects.filter(user=user, badge=badge).exists():
            UserBadge.objects.create(user=user, badge=badge, awarded_at=now())
            return True
        return False
    except Badge.DoesNotExist:
        return None

@login_required
def badges(request):
    """
    Unlock a badge when a user acquires a streak for all their habits
    """
    habits = Habit.objects.filter(user=request.user)

    has_first_habit = habits.exists()
    has_streak_3 = all(calculate_streak(habit) >= 3 for habit in habits)
    has_streak_7 = all(calculate_streak(habit) >= 7 for habit in habits)
    has_streak_30 = all(calculate_streak(habit) >= 30 for habit in habits)

    challenges = Challenge.objects.all()
    badges = UserBadge.objects.filter(user=request.user)
    joined_challenge_ids = UserChallenge.objects.filter(user=request.user).values_list('challenge_id', flat=True)

    check_challenge_completion(request.user)  # ✅ Auto update challenge status
    user_challenges = UserChallenge.objects.filter(user=request.user)

    # 🏅 Award badges if thresholds are met
    if has_streak_3:
        award_badge(request.user, "3-day-streak")

    if has_streak_7:
        award_badge(request.user, "7-day-streak")

    if has_streak_30:
        award_badge(request.user, "1-month-streak")

    context = {
        'has_first_habit': has_first_habit,
        'has_streak_3': has_streak_3,
        'has_streak_7': has_streak_7,
        'has_streak_30': has_streak_30,
        'challenges': challenges,
        'badges': badges,
        'joined_challenge_ids': list(joined_challenge_ids),
        'user_challenges': user_challenges,
    }
    return render(request, 'habits/badges.html', context)


def calculate_streak(habit):
    """
    Calculate the current streak of consecutive days a habit has been completed.
    """
    completions = habit.completions.filter(completed=True).order_by('-date').values_list('date', flat=True)
    
    if not completions:
        return 0
    streak = 1  # Start at 1 because the most recent date counts
    for i in range(1, len(completions)):
        prev_date = completions[i - 1]
        curr_date = completions[i]
        if (prev_date - curr_date).days == 1:
            streak += 1
        else:
            break  # Streak is broken
    return streak

# Habits

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

            award_badge(request.user, "first-habit-created")

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

@login_required
def habit_list(request):
    """
    Display a list of user-created habits
    """
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'habits/habit_list.html', {'habits': habits})

@login_required
def habit_edit(request, pk):
    """
    Edit habit form 
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)

    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habit updated successfully.')
            return redirect('habits:habit_list')
    else:
        form = HabitForm(instance=habit)

    return render(request, 'habits/habit_edit.html', {'form': form, 'habit': habit})

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
    today = date.today()

    #Active habits user has (To show if pending or completed)
    completed_habit_ids = HabitCompletion.objects.filter(
        habit__user=request.user,
        date=today,
        completed=True
    ).values_list('habit_id', flat=True)
    # Annotate each habit with a status for today
    for habit in habits:
        habit.status = "Done" if habit.id in completed_habit_ids else "Pending"
        
    # Weekly Bar Chart Data
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    weekly_data = HabitCompletion.objects.filter(
        habit__user=request.user,
        date__range=[week_dates[0], week_dates[-1]],
        completed=True
    ).values('date').annotate(count=Count('id'))
    chart_labels = [d.strftime('%a') for d in week_dates]
    chart_data = [next((item['count'] for item in weekly_data if item['date'] == d), 0) for d in week_dates]
   # Pie Chart Data - Completion by Category (today only)
    category_data = HabitCompletion.objects.filter(
        habit__user=request.user,
        date=today,
        completed=True
    ).values('habit__category').annotate(count=Count('id'))
    category_labels = []
    category_counts = []
    category_map = dict(Habit.CATEGORY_CHOICES)
    for item in category_data:
        label = category_map.get(item['habit__category'], 'Uncategorised')
        category_labels.append(label)
        category_counts.append(item['count'])
    # Today's stats
    completed_today = len(completed_habit_ids)
    habit_count = habits.count()
    notes_count = Note.objects.filter(user=request.user).count()
    pinned_notes = Note.objects.filter(user=request.user, is_pinned=True).order_by('-updated_at')
    return render(request, 'habits/dashboard.html', {
        'habits': habits,
        'completed_today': completed_today,
        'habit_count': habit_count,
        'today': today,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_counts),
        'notes_count': notes_count,
        'pinned_notes': pinned_notes,
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

def get_week_dates(current_date):
    """
    Calculate the Monday of the current week
    """
    start = current_date - timedelta(days=current_date.weekday())  # Monday
    return [start + timedelta(days=i) for i in range(7)]

@login_required
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
    habits = Habit.objects.filter(user=request.user).prefetch_related("completions")
    habit_data = []
    for habit in habits:
        completions = {}
        for day in week_dates:
            is_done = habit.completions.filter(date=day, completed=True).exists()
            completions[day.strftime("%Y-%m-%d")] = is_done
        habit_data.append({
            "habit": habit,
            "completions": completions
        })
    context = {
        "habits": habit_data,
        "week_dates": week_dates,
        "previous_week": current_date - timedelta(weeks=1),
        "next_week": current_date + timedelta(weeks=1),
    }

    return render(request, "habits/calendar.html", context)

@require_POST
def toggle_completion(request):
    """
    Toggle the completion status of a habit on a specific date.
    """
    try:
        data = json.loads(request.body)
        habit_id = data.get("habit_id")
        date_str = data.get("date")

        # Validate presence of required data
        if not habit_id or not date_str:
            return JsonResponse({"error": "Missing data"}, status=400)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        # Fetch the habit belonging to the logged-in user
        habit = Habit.objects.get(id=habit_id, user=request.user)
        try:
            # Try to get an existing HabitCompletion for the habit on the given date
            completion = HabitCompletion.objects.get(habit=habit, date=date)
            # Toggle the completed status (True → False or False → True)
            completion.completed = not completion.completed
            completion.save()

            return JsonResponse({"completed": completion.completed})
        
        except HabitCompletion.DoesNotExist:
            # No existing record: create one and mark as completed
            HabitCompletion.objects.create(habit=habit, date=date, completed=True)
            return JsonResponse({"completed": True})

    except Habit.DoesNotExist:
        # If the habit does not exist or doesn't belong to the user
        return JsonResponse({"error": "Habit not found"}, status=404)

    except Exception as e:
        # Catch any other errors and return a server error response
        return JsonResponse({"error": str(e)}, status=500)