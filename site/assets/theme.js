'use strict';

// Apply the page's default or saved theme before styles render.
(() => {
  const root = document.documentElement;
  const defaultTheme = ['synthwave', 'lemonade'].includes(root.dataset.defaultTheme) ? root.dataset.defaultTheme : 'nord';
  const lightTheme = defaultTheme === 'lemonade' ? 'lemonade' : 'nord';
  const darkTheme = defaultTheme === 'synthwave' ? 'synthwave' : 'night';
  const key = 'nicholas-roberts-theme' + (defaultTheme === 'nord' ? '' : ':' + defaultTheme);
  let theme = defaultTheme;
  try {
    const saved = localStorage.getItem(key);
    if (saved === lightTheme || saved === darkTheme) theme = saved;
  } catch (_) { /* Theme switching still works when storage is unavailable. */ }
  root.dataset.theme = theme;

  function updateChrome(value) {
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = value === 'synthwave' ? '#09002f' : value === 'night' ? '#0f1729' : value === 'lemonade' ? '#f8ffed' : '#eceff4';
  }
  updateChrome(theme);
  document.addEventListener('DOMContentLoaded', () => {
    const controller = document.querySelector('input.theme-controller');
    if (!controller) return;
    controller.checked = theme === darkTheme;
    controller.addEventListener('change', () => {
      theme = controller.checked ? darkTheme : lightTheme;
      root.dataset.theme = theme;
      updateChrome(theme);
      try { localStorage.setItem(key, theme); } catch (_) { /* Optional persistence. */ }
    });
  });
})();
