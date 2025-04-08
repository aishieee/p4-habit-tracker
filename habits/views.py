from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
