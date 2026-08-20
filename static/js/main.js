document.addEventListener('DOMContentLoaded', () => {
  console.log("Panchakanya JavaScript Loaded Successfully");

  // Mobile Menu Click Listener
  document.addEventListener('click', (e) => {
    const mobileMenu = document.getElementById('mobile-menu');

    // Open Menu Button
    if (e.target.closest('#mobile-menu-btn')) {
      if (mobileMenu) {
        mobileMenu.classList.remove('closed');
        mobileMenu.classList.add('open');
      }
    }

    // Close Menu Button
    if (e.target.closest('#close-menu-btn')) {
      if (mobileMenu) {
        mobileMenu.classList.remove('open');
        mobileMenu.classList.add('closed');
      }
    }

    // User Dropdown Toggle
    const userMenuBtn = e.target.closest('#user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    if (userMenuBtn && userDropdown) {
      userDropdown.classList.toggle('hidden');
    } else if (userDropdown && !e.target.closest('#user-dropdown')) {
      // Close dropdown if clicking outside
      userDropdown.classList.add('hidden');
    }
  });
});
