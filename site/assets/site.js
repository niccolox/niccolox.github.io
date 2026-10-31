'use strict';

document.documentElement.classList.add('js-ready');

const megamenu = document.querySelector('#site-megamenu');

// Popovers stay open on same-page links; close the menu once a destination is chosen.
megamenu?.addEventListener('click', (event) => {
  const link = event.target.closest('a');
  if (!link) return;
  megamenu.querySelectorAll('[popover]').forEach((panel) => {
    if (panel.matches(':popover-open')) panel.hidePopover();
  });
  if (megamenu.matches(':popover-open')) megamenu.hidePopover();
  const destination = new URL(link.href);
  if (destination.origin === location.origin && destination.pathname === location.pathname && destination.hash) {
    const target = document.getElementById(decodeURIComponent(destination.hash.slice(1)));
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }
  }
});

const year = document.querySelector('#year');
if (year) year.textContent = String(new Date().getFullYear());
document.querySelector('#print-resume')?.addEventListener('click', () => window.print());
