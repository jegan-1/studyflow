from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6366f1')
    goal_hours_per_week = models.FloatField(default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def total_hours_studied(self):
        sessions = self.study_sessions.all()
        total_minutes = sum(s.duration_minutes for s in sessions)
        return round(total_minutes / 60, 2)

    def this_week_hours(self):
        from datetime import timedelta
        week_start = timezone.now() - timedelta(days=7)
        sessions = self.study_sessions.filter(date__gte=week_start)
        total_minutes = sum(s.duration_minutes for s in sessions)
        return round(total_minutes / 60, 2)


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    estimated_minutes = models.IntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and self.status != 'done':
            return self.due_date < timezone.now().date()
        return False

    def save(self, *args, **kwargs):
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
        super().save(*args, **kwargs)


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_sessions')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_sessions')
    date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.IntegerField()
    notes = models.TextField(blank=True)
    mood = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    productivity = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])

    def __str__(self):
        return f"{self.subject.name} - {self.date.date()} ({self.duration_minutes}min)"

    @property
    def duration_hours(self):
        return round(self.duration_minutes / 60, 2)


class StudyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_hours = models.FloatField()
    current_hours = models.FloatField(default=0)
    deadline = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def progress_percent(self):
        if self.target_hours == 0:
            return 100
        return min(100, round((self.current_hours / self.target_hours) * 100, 1))

    @property
    def is_overdue(self):
        return self.deadline < timezone.now().date() and not self.is_completed
