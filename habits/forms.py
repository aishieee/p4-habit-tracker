from django import forms
from .models import Habit, HabitCompletion

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'target', 'frequency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class HabitCompletionForm(forms.ModelForm):
    class Meta:
        model = HabitCompletion
        fields = ['completed', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }