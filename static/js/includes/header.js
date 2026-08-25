document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('pk-js-mobile-toggle');
    const navBar = document.getElementById('pk-js-nav-bar');
    const userBtn = document.getElementById('pk-js-user-btn');
    const userDropdown = document.getElementById('pk-js-user-dropdown');
    const desktopNavigation = window.matchMedia('(min-width: 992px)');

    const setMobileMenu = (isOpen) => {
        if (!toggleBtn || !navBar) {
            return;
        }

        navBar.classList.toggle('pk-hdr-nav-bar--mobile-open', isOpen);
        toggleBtn.setAttribute('aria-expanded', String(isOpen));
        toggleBtn.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
    };

    if (toggleBtn && navBar) {
        toggleBtn.addEventListener('click', () => {
            setMobileMenu(!navBar.classList.contains('pk-hdr-nav-bar--mobile-open'));
        });

        navBar.addEventListener('click', (event) => {
            if (event.target.closest('.pk-hdr-nav-link')) {
                setMobileMenu(false);
            }
        });
    }

    if (userBtn && userDropdown) {
        const setUserDropdown = (isOpen) => {
            userDropdown.classList.toggle('pk-hdr-dropdown-menu--open', isOpen);
            userBtn.setAttribute('aria-expanded', String(isOpen));
        };

        userBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            setUserDropdown(!userDropdown.classList.contains('pk-hdr-dropdown-menu--open'));
        });

        document.addEventListener('click', (event) => {
            if (!userDropdown.contains(event.target) && !userBtn.contains(event.target)) {
                setUserDropdown(false);
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                setUserDropdown(false);
            }
        });
    }

    if (navBar) {
        const scrollThreshold = 12;
        let lastScrollY = window.scrollY;
        let downwardDistance = 0;
        let upwardDistance = 0;
        let animationFrame = null;

        const updateNavigationVisibility = () => {
            const currentScrollY = Math.max(window.scrollY, 0);
            const scrollDifference = currentScrollY - lastScrollY;

            if (!desktopNavigation.matches || currentScrollY <= 80) {
                navBar.classList.remove('pk-hdr-nav-bar--hidden');
                downwardDistance = 0;
                upwardDistance = 0;
            } else if (scrollDifference > 0) {
                downwardDistance += scrollDifference;
                upwardDistance = 0;

                if (downwardDistance >= scrollThreshold) {
                    navBar.classList.add('pk-hdr-nav-bar--hidden');
                }
            } else if (scrollDifference < 0) {
                upwardDistance += Math.abs(scrollDifference);
                downwardDistance = 0;

                if (upwardDistance >= scrollThreshold) {
                    navBar.classList.remove('pk-hdr-nav-bar--hidden');
                }
            }

            lastScrollY = currentScrollY;
            animationFrame = null;
        };

        window.addEventListener('scroll', () => {
            if (animationFrame === null) {
                animationFrame = window.requestAnimationFrame(updateNavigationVisibility);
            }
        }, { passive: true });

        const resetNavigationOnViewportChange = () => {
            navBar.classList.remove('pk-hdr-nav-bar--hidden');
            setMobileMenu(false);
            lastScrollY = window.scrollY;
            downwardDistance = 0;
            upwardDistance = 0;
        };

        if (desktopNavigation.addEventListener) {
            desktopNavigation.addEventListener('change', resetNavigationOnViewportChange);
        } else {
            desktopNavigation.addListener(resetNavigationOnViewportChange);
        }
    }
});
