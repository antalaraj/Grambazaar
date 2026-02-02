document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.dashboard-notifications');
  if (!container) return;

  const pollUrl = container.dataset.pollUrl;
  const listEl = document.getElementById('notif-list');
  const countEl = document.getElementById('notif-count');

  async function poll() {
    try {
      const res = await fetch(pollUrl);
      const data = await res.json();
      const items = data.notifications || [];

      if (!items.length) {
        listEl.innerHTML = `
          <div class="text-center p-3">
            <p class="text-muted small mb-0">No new notifications.</p>
          </div>
        `;
        countEl.style.display = 'none';
        return;
      }

      let html = '';
      items.forEach(n => {
        html += `
          <div class="list-group-item notification-item" data-notif-id="${n.id}">
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1">${n.title}</h6>
              <small class="text-muted">${n.created_at}</small>
            </div>
            <p class="mb-1 small">${n.message}</p>
            <div class="d-flex justify-content-between align-items-center mt-1">
              <small class="text-muted">Targeted to your SHG</small>
              <button class="btn btn-outline-secondary btn-sm" data-notif-id="${n.id}">Mark as read</button>
            </div>
          </div>
        `;
      });

      listEl.innerHTML = html;
      countEl.textContent = items.length;
      countEl.style.display = '';
    } catch (e) {
      // ignore polling errors
    }
  }

  poll();
  setInterval(poll, 15000);
});
