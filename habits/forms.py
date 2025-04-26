from django import forms
from .models import Habit, HabitCompletion
from django.core.exceptions import ValidationError

# Create and edit habits
class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit  
        fields = ['name', 'description', 'target', 'frequency']  # Fields to show in the form
        widgets = {  
            'name': forms.TextInput(attrs={'class': 'form-control'}),  # Bootstrap styling
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'target': forms.NumberInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }
    
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
    
    # Custom validation: Check if this user already has a habit with the same name
    def clean_name(self):
        name = self.cleaned_data['name']  # Get the submitted habit name
        if self.user and Habit.objects.filter(user=self.user, name=name).exists():
            if self.instance.pk:  # If editing an existing habit
                if Habit.objects.filter(user=self.user, name=name).exclude(pk=self.instance.pk).exists():
                    raise ValidationError("You already have a habit with this name.")
            else:  # If creating a new habit
                raise ValidationError("You already have a habit with this name.")
        return name  # Return the valid name

# Mark habits as completed
class HabitCompletionForm(forms.ModelForm):
    class Meta:
        model = HabitCompletion  
        fields = ['completed', 'notes'] 
        widgets = {  
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),  # Bootstrap styling
        }
