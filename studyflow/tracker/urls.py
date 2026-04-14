from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('subjects/', views.subjects_view, name='subjects'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/update/<int:pk>/', views.update_task_status, name='update_task'),
    path('tasks/delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('sessions/', views.sessions_view, name='sessions'),
    path('sessions/delete/<int:pk>/', views.delete_session, name='delete_session'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('goals/', views.goals_view, name='goals'),
    path('api/timer-session/', views.api_timer_session, name='api_timer_session'),
]
