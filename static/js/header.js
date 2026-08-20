   document.addEventListener('DOMContentLoaded', function() {
        // Mobile menu toggle
        const toggleBtn = document.getElementById('pk-js-mobile-toggle');
        const navBar = document.getElementById('pk-js-nav-bar');

        if (toggleBtn && navBar) {
            toggleBtn.addEventListener('click', function() {
                navBar.classList.toggle('pk-nav-mobile-open');
            });
        }

        // Account dropdown toggle for logged-in users
        const userBtn = document.getElementById('pk-js-user-btn');
        const userDropdown = document.getElementById('pk-js-user-dropdown');

        if (userBtn && userDropdown) {
            userBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                userDropdown.classList.toggle('pk-dropdown-open');
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!userDropdown.contains(e.target) && !userBtn.contains(e.target)) {
                    userDropdown.classList.remove('pk-dropdown-open');
                }
            });
        }
    });
