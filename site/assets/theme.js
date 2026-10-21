'use strict';

// Apply the saved theme before styles render. Nord is the default everywhere.
(() => {
  const root = document.documentElement;
  const key = 'nicholas-roberts-theme';
  let theme = 'nord';
  try {
    if (localStorage.getItem(key) === 'night') theme = 'night';
  } catch (_) { /* Theme switching still works when storage is unavailable. */ }
  root.dataset.theme = theme;

  function updateChrome(value) {
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = value === 'night' ? '#0f1729' : '#eceff4';
  }
  updateChrome(theme);
  document.addEventListener('DOMContentLoaded', () => {
    const controller = document.querySelector('input.theme-controller');
    if (!controller) return;
    controller.checked = theme === 'night';
    controller.addEventListener('change', () => {
      theme = controller.checked ? 'night' : 'nord';
      root.dataset.theme = theme;
      updateChrome(theme);
      try { localStorage.setItem(key, theme); } catch (_) { /* Optional persistence. */ }
    });
  });
})();
