'use strict';

document.documentElement.classList.add('js-ready');

const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');

function closeMenu() {
  menu?.setAttribute('aria-expanded', 'false');
  navigation?.classList.remove('is-open');
}

menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  navigation.classList.toggle('is-open', open);
});

navigation?.addEventListener('click', (event) => {
  const link = event.target.closest('a');
  if (!link) return;
  closeMenu();
  const destination = new URL(link.href);
  if (destination.origin === location.origin && destination.pathname === location.pathname && destination.hash) {
    const target = document.getElementById(decodeURIComponent(destination.hash.slice(1)));
    if (target) {
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menu.focus();
  }
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('.site-header')) closeMenu();
});

document.querySelector('.site-header')?.addEventListener('focusout', (event) => {
  if (event.relatedTarget && !event.currentTarget.contains(event.relatedTarget)) closeMenu();
});

window.matchMedia('(min-width: 1101px)').addEventListener('change', closeMenu);
const year = document.querySelector('#year');
if (year) year.textContent = String(new Date().getFullYear());
document.querySelector('#print-resume')?.addEventListener('click', () => window.print());
