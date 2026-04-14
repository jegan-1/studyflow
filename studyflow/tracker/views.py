from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta, date
import json
from .models import Subject, Task, StudySession, StudyGoal


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create sample subjects for new users
            colors = ['#6366f1', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']
            subjects_data = [
                ('Mathematics', '#6366f1', 8),
                ('Physics', '#f59e0b', 6),
                ('History', '#10b981', 4),
            ]
            for name, color, goal in subjects_data:
                Subject.objects.create(user=user, name=name, color=color, goal_hours_per_week=goal)
            messages.success(request, 'Account created! Welcome aboard.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    now = timezone.now()
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    subjects = Subject.objects.filter(user=user)
    tasks = Task.objects.filter(user=user).order_by('-created_at')
    recent_sessions = StudySession.objects.filter(user=user).order_by('-date')[:10]
    goals = StudyGoal.objects.filter(user=user, is_completed=False).order_by('deadline')[:5]

    # Stats
    total_sessions = StudySession.objects.filter(user=user).count()
    week_minutes = StudySession.objects.filter(user=user, date__gte=week_start).aggregate(
        total=Sum('duration_minutes'))['total'] or 0
    month_minutes = StudySession.objects.filter(user=user, date__gte=month_start).aggregate(
        total=Sum('duration_minutes'))['total'] or 0

    tasks_due_soon = Task.objects.filter(
        user=user, status__in=['todo', 'in_progress'],
        due_date__lte=(now + timedelta(days=3)).date()
    ).order_by('due_date')

    overdue_tasks = [t for t in tasks if t.is_overdue()]

    # Chart data - last 7 days study hours
    daily_data = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_minutes = StudySession.objects.filter(
            user=user, date__date=day
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        daily_data.append({
            'date': day.strftime('%a'),
            'hours': round(day_minutes / 60, 2)
        })

    # Subject breakdown
    subject_data = []
    for subj in subjects:
        hours = subj.this_week_hours()
        subject_data.append({'name': subj.name, 'hours': hours, 'color': subj.color})

    context = {
        'subjects': subjects,
        'tasks': tasks[:8],
        'recent_sessions': recent_sessions,
        'goals': goals,
        'total_sessions': total_sessions,
        'week_hours': round(week_minutes / 60, 2),
        'month_hours': round(month_minutes / 60, 2),
        'tasks_due_soon': tasks_due_soon,
        'overdue_count': len(overdue_tasks),
        'daily_chart_data': json.dumps(daily_data),
        'subject_chart_data': json.dumps(subject_data),
        'tasks_todo': tasks.filter(status='todo').count(),
        'tasks_done': tasks.filter(status='done').count(),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def subjects_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#6366f1')
        goal = request.POST.get('goal_hours', 5)
        Subject.objects.create(user=request.user, name=name, color=color, goal_hours_per_week=float(goal))
        messages.success(request, f'Subject "{name}" created!')
        return redirect('subjects')

    subjects = Subject.objects.filter(user=request.user).annotate(
        session_count=Count('study_sessions')
    )
    subject_stats = []
    for s in subjects:
        subject_stats.append({
            'obj': s,
            'total_hours': s.total_hours_studied(),
            'week_hours': s.this_week_hours(),
            'task_count': s.tasks.count(),
        })
    return render(request, 'tracker/subjects.html', {'subject_stats': subject_stats})


@login_required
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk, user=request.user)
    subject.delete()
    messages.success(request, 'Subject deleted.')
    return redirect('subjects')


@login_required
def tasks_view(request):
    if request.method == 'POST':
        Task.objects.create(
            user=request.user,
            subject_id=request.POST.get('subject') or None,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            priority=request.POST.get('priority', 'medium'),
            due_date=request.POST.get('due_date') or None,
            estimated_minutes=int(request.POST.get('estimated_minutes', 60)),
        )
        messages.success(request, 'Task created!')
        return redirect('tasks')

    status_filter = request.GET.get('status', 'all')
    tasks = Task.objects.filter(user=request.user)
    if status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    tasks = tasks.order_by('-created_at')
    subjects = Subject.objects.filter(user=request.user)

    return render(request, 'tracker/tasks.html', {
        'tasks': tasks,
        'subjects': subjects,
        'status_filter': status_filter,
    })


@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        task.status = data.get('status', task.status)
        task.save()
        return JsonResponse({'success': True, 'status': task.status})
    return JsonResponse({'error': 'Invalid'}, status=400)


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted.')
    return redirect('tasks')


@login_required
def sessions_view(request):
    if request.method == 'POST':
        StudySession.objects.create(
            user=request.user,
            subject_id=request.POST.get('subject'),
            task_id=request.POST.get('task') or None,
            duration_minutes=int(request.POST.get('duration_minutes', 60)),
            notes=request.POST.get('notes', ''),
            mood=int(request.POST.get('mood', 3)),
            productivity=int(request.POST.get('productivity', 3)),
            date=request.POST.get('date') or timezone.now(),
        )
        messages.success(request, 'Study session logged!')
        return redirect('sessions')

    sessions = StudySession.objects.filter(user=request.user).order_by('-date')[:50]
    subjects = Subject.objects.filter(user=request.user)
    tasks = Task.objects.filter(user=request.user, status__in=['todo', 'in_progress'])

    return render(request, 'tracker/sessions.html', {
        'sessions': sessions,
        'subjects': subjects,
        'tasks': tasks,
    })


@login_required
def delete_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk, user=request.user)
    session.delete()
    messages.success(request, 'Session deleted.')
    return redirect('sessions')


@login_required
def analytics_view(request):
    user = request.user
    now = timezone.now()

    # Last 30 days daily hours
    daily_data = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_minutes = StudySession.objects.filter(
            user=user, date__date=day
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        daily_data.append({'date': day.strftime('%b %d'), 'hours': round(day_minutes / 60, 2)})

    # Subject totals
    subjects = Subject.objects.filter(user=user)
    subject_totals = []
    for s in subjects:
        mins = StudySession.objects.filter(user=user, subject=s).aggregate(
            total=Sum('duration_minutes'))['total'] or 0
        subject_totals.append({'name': s.name, 'hours': round(mins / 60, 2), 'color': s.color})

    # Avg productivity by subject
    productivity_data = []
    for s in subjects:
        avg = StudySession.objects.filter(user=user, subject=s).aggregate(
            avg=Avg('productivity'))['avg'] or 0
        productivity_data.append({'name': s.name, 'avg': round(avg, 2), 'color': s.color})

    # Mood trend last 14 days
    mood_data = []
    for i in range(13, -1, -1):
        day = (now - timedelta(days=i)).date()
        avg_mood = StudySession.objects.filter(
            user=user, date__date=day
        ).aggregate(avg=Avg('mood'))['avg']
        mood_data.append({'date': day.strftime('%b %d'), 'mood': round(avg_mood, 2) if avg_mood else None})

    # Heatmap - last 52 weeks
    heatmap_data = {}
    for i in range(364, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_minutes = StudySession.objects.filter(
            user=user, date__date=day
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        heatmap_data[str(day)] = round(day_minutes / 60, 2)

    # Overall stats
    total_sessions = StudySession.objects.filter(user=user).count()
    total_minutes = StudySession.objects.filter(user=user).aggregate(
        total=Sum('duration_minutes'))['total'] or 0
    avg_session_minutes = StudySession.objects.filter(user=user).aggregate(
        avg=Avg('duration_minutes'))['avg'] or 0
    completed_tasks = Task.objects.filter(user=user, status='done').count()
    total_tasks = Task.objects.filter(user=user).count()

    # Best streak
    streak = 0
    best_streak = 0
    current_streak = 0
    check_day = now.date()
    while True:
        has_session = StudySession.objects.filter(user=user, date__date=check_day).exists()
        if has_session:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            if check_day == now.date():
                pass
            else:
                break
        check_day -= timedelta(days=1)
        if current_streak > 365:
            break

    context = {
        'daily_data': json.dumps(daily_data),
        'subject_totals': json.dumps(subject_totals),
        'productivity_data': json.dumps(productivity_data),
        'mood_data': json.dumps(mood_data),
        'heatmap_data': json.dumps(heatmap_data),
        'total_sessions': total_sessions,
        'total_hours': round(total_minutes / 60, 2),
        'avg_session_min': round(avg_session_minutes, 0),
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'current_streak': current_streak,
        'best_streak': best_streak,
    }
    return render(request, 'tracker/analytics.html', context)


@login_required
def goals_view(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject') or None
        goal = StudyGoal.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            target_hours=float(request.POST.get('target_hours', 10)),
            deadline=request.POST.get('deadline'),
            subject_id=subject_id,
        )
        # Update current hours from existing sessions
        if subject_id:
            mins = StudySession.objects.filter(
                user=request.user, subject_id=subject_id
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0
            goal.current_hours = round(mins / 60, 2)
            goal.save()
        messages.success(request, 'Goal created!')
        return redirect('goals')

    goals = StudyGoal.objects.filter(user=request.user).order_by('deadline')
    subjects = Subject.objects.filter(user=request.user)

    # Update current hours for all goals
    for goal in goals:
        if goal.subject:
            mins = StudySession.objects.filter(
                user=request.user, subject=goal.subject
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0
            goal.current_hours = round(mins / 60, 2)
            if goal.current_hours >= goal.target_hours:
                goal.is_completed = True
            goal.save()

    return render(request, 'tracker/goals.html', {'goals': goals, 'subjects': subjects})


@login_required
def api_timer_session(request):
    """Quick API endpoint for Pomodoro timer to log sessions."""
    if request.method == 'POST':
        data = json.loads(request.body)
        subject_id = data.get('subject_id')
        duration = data.get('duration_minutes', 25)
        if subject_id:
            session = StudySession.objects.create(
                user=request.user,
                subject_id=subject_id,
                duration_minutes=duration,
                notes='Logged via Pomodoro timer',
                mood=3,
                productivity=3,
            )
            return JsonResponse({'success': True, 'session_id': session.id})
    return JsonResponse({'error': 'Invalid'}, status=400)
