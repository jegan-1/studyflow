from django.contrib import admin
from .models import Subject, Task, StudySession, StudyGoal

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'goal_hours_per_week', 'created_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'subject', 'priority', 'status', 'due_date']
    list_filter = ['status', 'priority']

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'date', 'duration_minutes', 'mood', 'productivity']

@admin.register(StudyGoal)
class StudyGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'target_hours', 'current_hours', 'deadline', 'is_completed']
