# 📚 StudyFlow — Study Planner & Tracker Analytics

A full-featured academic productivity app built with Django, Python, HTML, CSS, JavaScript, and SQLite.

---

## ✨ Features

- **Dashboard** — Weekly stats, daily study hours bar chart, subject breakdown doughnut chart
- **Subjects** — Create subjects with custom colors, weekly hour goals, and progress tracking
- **Tasks** — Full task manager with priority levels, due dates, overdue detection, inline AJAX status updates
- **Study Sessions** — Log study time with mood & productivity ratings (1–5), link to tasks
- **Analytics** — 30-day line chart, GitHub-style activity heatmap, productivity & mood trends by subject
- **Goals** — Set target hours with deadlines, auto-tracks progress from sessions
- **Pomodoro Timer** — Floating 25-min timer widget that auto-logs sessions on completion
- **Auth** — Register/login with sample subjects auto-created for new users

---

## 🚀 Quick Start

### 1. Install Django
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations tracker
python manage.py migrate
```

### 3. (Optional) Create admin superuser
```bash
python manage.py createsuperuser
```

### 4. Start the server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/register/
```

Register a new account — three sample subjects (Mathematics, Physics, History) are automatically created.

---

## 📁 Project Structure

```
studyplanner/
├── manage.py
├── requirements.txt
├── db.sqlite3              ← created after migrate
├── studyplanner/
│   ├── settings.py         ← project config (SQLite, auth)
│   ├── urls.py             ← root URL routing
│   └── wsgi.py
└── tracker/                ← main app
    ├── models.py           ← Subject, Task, StudySession, StudyGoal
    ├── views.py            ← all views + analytics aggregations
    ├── urls.py             ← app URL patterns
    ├── admin.py            ← Django admin registrations
    ├── apps.py
    └── templates/tracker/
        ├── base.html       ← sidebar layout + Pomodoro widget
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── analytics.html
        ├── subjects.html
        ├── tasks.html
        ├── sessions.html
        └── goals.html
```

---

## 🗃️ Database Models (SQL via Django ORM)

| Model | Key Fields |
|-------|-----------|
| `Subject` | name, color, goal_hours_per_week |
| `Task` | title, priority, status, due_date, estimated_minutes |
| `StudySession` | subject, duration_minutes, mood, productivity, notes |
| `StudyGoal` | title, target_hours, deadline, progress tracking |

All models are linked to Django's built-in `User` model.

---

## 🔧 Tech Stack

- **Backend**: Django 4.2+, Python 3.10+
- **Database**: SQLite (via Django ORM — swap to PostgreSQL by changing `DATABASES` in settings.py)
- **Frontend**: Vanilla HTML/CSS/JS + Chart.js (CDN)
- **Auth**: Django built-in authentication
- **Fonts**: DM Serif Display + DM Sans (Google Fonts)

---

## 🌐 Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | dashboard | Main overview |
| `/register/` | register | Create account |
| `/login/` | login | Sign in |
| `/subjects/` | subjects_view | Manage subjects |
| `/tasks/` | tasks_view | Task manager |
| `/sessions/` | sessions_view | Study sessions log |
| `/analytics/` | analytics_view | Charts & insights |
| `/goals/` | goals_view | Goal tracking |
| `/api/timer-session/` | api_timer_session | Pomodoro POST endpoint |
| `/admin/` | Django admin | Admin panel |

---

## 💡 Tips

- Use `?status=todo` / `?status=in_progress` / `?status=done` on `/tasks/` to filter
- Click task status dropdown to update inline (AJAX, no page reload)
- The Pomodoro widget in the bottom-right auto-logs a 25-min session when timer completes
- Admin panel at `/admin/` gives full data management (requires superuser)
