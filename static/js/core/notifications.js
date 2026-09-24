/**
 * CodeForge IDE - Toast Notification System
 */

class Toast {
  static container = null;

  static init() {
    if (!Toast.container) {
      let el = document.getElementById('toast-container');
      if (!el) {
        el = document.createElement('div');
        el.id = 'toast-container';
        document.body.appendChild(el);
      }
      Toast.container = el;
    }
  }

  static show(message, type = 'info', duration = 3500) {
    Toast.init();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconHtml = '<i data-lucide="info"></i>';
    if (type === 'success') iconHtml = '<i data-lucide="check-circle" style="color: var(--success);"></i>';
    if (type === 'error') iconHtml = '<i data-lucide="alert-circle" style="color: var(--error);"></i>';
    if (type === 'warning') iconHtml = '<i data-lucide="alert-triangle" style="color: var(--warning);"></i>';

    toast.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;width:100%;">
        ${iconHtml}
        <span style="flex:1;">${message}</span>
        <button style="background:none;border:none;color:var(--text-dim);cursor:pointer;padding:2px;" onclick="this.parentElement.parentElement.remove()">
          <i data-lucide="x" style="width:14px;height:14px;"></i>
        </button>
      </div>
    `;

    Toast.container.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
      toast.style.transition = 'all 200ms ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px) scale(0.95)';
      setTimeout(() => toast.remove(), 200);
    }, duration);
  }

  static success(msg, dur) { Toast.show(msg, 'success', dur); }
  static error(msg, dur) { Toast.show(msg, 'error', dur); }
  static warning(msg, dur) { Toast.show(msg, 'warning', dur); }
  static info(msg, dur) { Toast.show(msg, 'info', dur); }
}

window.Toast = Toast;
