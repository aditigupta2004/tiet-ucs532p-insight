/* Smart Parking Spot Detection System — Main JS */

// ── Theme Toggle ──────────────────────────────────
const toggle = document.getElementById('themeToggle');
const html = document.documentElement;

const saved = localStorage.getItem('smart-parking-theme') || 'dark';
html.setAttribute('data-theme', saved);

toggle.addEventListener('click', () => {
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('smart-parking-theme', next);
});

// ── Sidebar Mobile ────────────────────────────────
const sidebar = document.getElementById('sidebar');
const hamburger = document.getElementById('hamburger');
const overlay = document.getElementById('overlay');

hamburger.addEventListener('click', () => {
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
});
overlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
});

// ── Scroll Spy ────────────────────────────────────
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-item[data-section]');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navItems.forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === entry.target.id) {
          item.classList.add('active');
        }
      });
    }
  });
}, { rootMargin: '-40% 0px -50% 0px' });

sections.forEach(s => observer.observe(s));

// ── Nav click: close mobile sidebar ──────────────
navItems.forEach(item => {
  item.addEventListener('click', () => {
    if (window.innerWidth < 900) {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    }
  });
});
