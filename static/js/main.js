/**
 * SolarLink Platform - Interactive Client Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Navigation Toggle
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('show');
    });
  }

  // User Account Dropdown Toggle
  const userMenuBtn = document.querySelector('.user-menu-btn');
  const dropdownPane = document.querySelector('.dropdown-pane');

  if (userMenuBtn && dropdownPane) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdownPane.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!dropdownPane.contains(e.target) && !userMenuBtn.contains(e.target)) {
        dropdownPane.classList.remove('show');
      }
    });
  }

  // Auto-dismiss Flash Alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-6px)';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });
});
