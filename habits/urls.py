from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'habits'

# URLs
urlpatterns = [
    # Habit List (homepage for habits)
    path('', login_required(views.habit_list), name='habit_list'),
    
    # Habit CRUD operations
    path('create/', login_required(views.habit_create), name='habit_create'),
    path('<int:pk>/', login_required(views.habit_detail), name='habit_detail'),
    path('<int:pk>/update/', login_required(views.habit_update), name='habit_update'),
    path('<int:pk>/delete/', login_required(views.habit_delete), name='habit_delete'),
    
    # Completion tracking
    path('<int:habit_id>/log/', login_required(views.log_completion), name='log_completion'),

    #User authentication 
    
]
