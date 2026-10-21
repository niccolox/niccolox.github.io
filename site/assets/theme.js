'use strict';

// Apply the page's default or saved theme before styles render.
(() => {
  const root = document.documentElement;
  const defaultTheme = root.dataset.defaultTheme === 'synthwave' ? 'synthwave' : 'nord';
  const darkTheme = defaultTheme === 'synthwave' ? 'synthwave' : 'night';
  const key = 'nicholas-roberts-theme' + (defaultTheme === 'synthwave' ? ':synthwave' : '');
  let theme = defaultTheme;
  try {
    const saved = localStorage.getItem(key);
    if (saved === 'nord' || saved === darkTheme) theme = saved;
  } catch (_) { /* Theme switching still works when storage is unavailable. */ }
  root.dataset.theme = theme;

  function updateChrome(value) {
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = value === 'synthwave' ? '#09002f' : value === 'night' ? '#0f1729' : '#eceff4';
  }
  updateChrome(theme);
  document.addEventListener('DOMContentLoaded', () => {
    const controller = document.querySelector('input.theme-controller');
    if (!controller) return;
    controller.checked = theme === darkTheme;
    controller.addEventListener('change', () => {
      theme = controller.checked ? darkTheme : 'nord';
      root.dataset.theme = theme;
      updateChrome(theme);
      try { localStorage.setItem(key, theme); } catch (_) { /* Optional persistence. */ }
    });
  });
})();
