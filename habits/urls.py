from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from .views import calendar_view
from .views import toggle_completion

app_name = 'habits'

# URLs
urlpatterns = [
    # Habit List (homepage for habits)
   

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<int:pk>/toggle/', views.toggle_habit, name='toggle_habit'),

    # Notes card
    path('notes/add/', views.add_note, name='add_note'),
    path('notes/', views.note_list, name='note_list'),
    path('notes/<int:pk>/edit/', views.edit_note, name='edit_note'),
    path('notes/<int:pk>/delete/', views.delete_note, name='delete_note'),

    # Habit CRUD operations
    path('create/', login_required(views.habit_create), name='habit_create'),
    path('<int:pk>/', login_required(views.habit_detail), name='habit_detail'),
    path('<int:pk>/update/', login_required(views.habit_update), name='habit_update'),
    path('<int:pk>/delete/', login_required(views.habit_delete), name='habit_delete'),
    
    # Completion tracking
    path('<int:habit_id>/log/', login_required(views.log_completion), name='log_completion'),
    path("calendar/", login_required(calendar_view), name="calendar"),
    path('api/toggle-completion/', toggle_completion, name='toggle_completion'),

    #User authentication 
    
]
