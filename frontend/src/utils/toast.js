// frontend/src/utils/toast.js
let container;

function ensureContainer() {
  if (!container) {
    container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.right = '16px';
    container.style.bottom = '16px';
    container.style.zIndex = '99999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '8px';
    document.body.appendChild(container);
  }
}

export function toast(message, type = 'info', ms = 2500) {
  ensureContainer();
  const el = document.createElement('div');
  el.textContent = message;
  el.style.padding = '10px 14px';
  el.style.borderRadius = '8px';
  el.style.fontSize = '14px';
  el.style.color = '#fff';
  el.style.border = '1px solid rgba(255,255,255,.15)';
  el.style.boxShadow = '0 2px 8px rgba(0,0,0,.25)';
  el.style.background = type === 'error' ? '#b64c4c' : (type === 'success' ? '#2c7a4b' : '#2a2a2a');
  el.style.opacity = '0';
  el.style.transform = 'translateY(8px)';
  el.style.transition = 'all .2s ease';
  container.appendChild(el);
  requestAnimationFrame(() => {
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  });
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
    setTimeout(() => el.remove(), 200);
  }, ms);
}
