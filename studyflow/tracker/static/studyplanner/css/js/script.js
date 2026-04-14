document.addEventListener('DOMContentLoaded', function () {

  // Toggle task completion via AJAX
  document.querySelectorAll('.task-check').forEach(btn => {
    btn.addEventListener('click', function () {
      const taskId = this.dataset.taskId;
      const newStatus = this.classList.contains('done') ? 'pending' : 'completed';

      fetch(`/tasks/${taskId}/toggle/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${newStatus}`
      })
        .then(r => r.json())
        .then(data => {
          if (data.status === 'ok') {
            this.classList.toggle('done');
            const item = this.closest('.task-item');
            newStatus === 'completed' ? item.classList.add('completed') : item.classList.remove('completed');
          }
        });
    });
  });

  // Auto-dismiss alerts
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s';
      setTimeout(() => alert.remove(), 500);
    }, 3500);
  });

  // Stagger animations
  document.querySelectorAll('.task-item').forEach((el, i) => el.style.animationDelay = `${i * 40}ms`);
  document.querySelectorAll('.stat-card').forEach((el, i) => el.style.animationDelay = `${i * 60}ms`);
});

function getCookie(name) {
  let val = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(c => {
      c = c.trim();
      if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
    });
  }
  return val;
}

function confirmDelete(form, name) {
  if (confirm(`Delete "${name}"? This cannot be undone.`)) form.submit();
}