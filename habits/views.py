from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages  

# Create your views here.
@login_required
def habit_list(request):
    """
    Display a list of the user's habits along with their streak and completion rate.
    """
    habits = Habit.objects.filter(user=request.user)
    template_habits = Habit.objects.filter(is_template=True)
    
    habits_with_streaks = [
        {
            'habit': habit,
            'streak': calculate_streak(habit),
            'completion_rate': habit.completions.filter(completed=True).count() / habit.target if habit.target > 0 else 0
        }
        for habit in habits
    ]
    
    return render(request, 'habits/habit_list.html', {
        'habits': habits_with_streaks,
        'template_habits': template_habits
    })

@login_required
def habit_create(request):
    """
    Handle the creation of a new habit.
    """
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit created successfully!')
            return redirect('habit_list')
    else:
        form = HabitForm()
    
    return render(request, 'habits/habit_form.html', {'form': form})

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
            return redirect('habit_list')
    else:
        form = HabitForm(instance=habit)
    
    return render(request, 'habits/habit_form.html', {'form': form})

@login_required
def habit_delete(request, pk):
    """
    Handle deleting an existing habit.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('habit_list')
    
    return render(request, 'habits/habit_confirm_delete.html', {'habit': habit})

