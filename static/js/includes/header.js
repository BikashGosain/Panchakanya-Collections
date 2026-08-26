document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById(
        'pk-js-mobile-toggle'
    );

    const navBar = document.getElementById(
        'pk-js-nav-bar'
    );

    const userBtn = document.getElementById(
        'pk-js-user-btn'
    );

    const userDropdown = document.getElementById(
        'pk-js-user-dropdown'
    );

    const desktopNavigation = window.matchMedia(
        '(min-width: 992px)'
    );


    /* ============================================================
       MOBILE MENU
       ============================================================ */

    const setMobileMenu = (isOpen) => {
        if (!toggleBtn || !navBar) {
            return;
        }

        navBar.classList.toggle(
            'pk-hdr-nav-bar--mobile-open',
            isOpen
        );

        toggleBtn.setAttribute(
            'aria-expanded',
            String(isOpen)
        );

        toggleBtn.setAttribute(
            'aria-label',
            isOpen
                ? 'Close navigation menu'
                : 'Open navigation menu'
        );
    };


    if (toggleBtn && navBar) {
        toggleBtn.addEventListener('click', () => {
            const isOpen =
                navBar.classList.contains(
                    'pk-hdr-nav-bar--mobile-open'
                );

            setMobileMenu(!isOpen);
        });


        navBar.addEventListener('click', (event) => {
            if (
                event.target.closest(
                    '.pk-hdr-nav-link'
                )
            ) {
                setMobileMenu(false);
            }
        });
    }


    /* ============================================================
       USER DROPDOWN
       ============================================================ */

    if (userBtn && userDropdown) {
        const setUserDropdown = (isOpen) => {
            userDropdown.classList.toggle(
                'pk-hdr-dropdown-menu--open',
                isOpen
            );

            userBtn.setAttribute(
                'aria-expanded',
                String(isOpen)
            );
        };


        userBtn.addEventListener('click', (event) => {
            event.stopPropagation();

            const isOpen =
                userDropdown.classList.contains(
                    'pk-hdr-dropdown-menu--open'
                );

            setUserDropdown(!isOpen);
        });


        document.addEventListener('click', (event) => {
            if (
                !userDropdown.contains(event.target) &&
                !userBtn.contains(event.target)
            ) {
                setUserDropdown(false);
            }
        });


        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                setUserDropdown(false);
            }
        });
    }


    /* ============================================================
       DESKTOP NAVIGATION SCROLL
       ============================================================ */

    if (navBar) {
        let lastScrollY = Math.max(
            window.scrollY,
            0
        );

        let scrollAccumulator = 0;

        let navigationHidden = false;


        /*
         * Do not react to tiny movements.
         */
        const SCROLL_THRESHOLD = 15;


        /*
         * Navigation stays visible near the top.
         */
        const TOP_THRESHOLD = 80;


        /* --------------------------------------------------------
           SHOW
           -------------------------------------------------------- */

        const showNavigation = () => {
            if (!navigationHidden) {
                return;
            }

            navBar.classList.remove(
                'pk-hdr-nav-bar--hidden'
            );

            navigationHidden = false;
        };


        /* --------------------------------------------------------
           HIDE
           -------------------------------------------------------- */

        const hideNavigation = () => {
            if (navigationHidden) {
                return;
            }

            navBar.classList.add(
                'pk-hdr-nav-bar--hidden'
            );

            navigationHidden = true;
        };


        /* --------------------------------------------------------
           SCROLL
           -------------------------------------------------------- */

        const handleScroll = () => {
            /*
             * Mobile never uses this behavior.
             */
            if (!desktopNavigation.matches) {
                showNavigation();

                scrollAccumulator = 0;

                lastScrollY = Math.max(
                    window.scrollY,
                    0
                );

                return;
            }


            const currentScrollY = Math.max(
                window.scrollY,
                0
            );


            /*
             * Always show at the very top.
             */
            if (currentScrollY <= TOP_THRESHOLD) {
                showNavigation();

                scrollAccumulator = 0;

                lastScrollY = currentScrollY;

                return;
            }


            const delta =
                currentScrollY - lastScrollY;


            /*
             * Ignore browser jitter.
             */
            if (Math.abs(delta) < 1) {
                return;
            }


            /*
             * Scrolling DOWN.
             */
            if (delta > 0) {
                scrollAccumulator += delta;


                if (
                    scrollAccumulator >=
                    SCROLL_THRESHOLD
                ) {
                    hideNavigation();

                    scrollAccumulator = 0;
                }
            }


            /*
             * Scrolling UP.
             */
            if (delta < 0) {
                scrollAccumulator += delta;


                if (
                    scrollAccumulator <=
                    -SCROLL_THRESHOLD
                ) {
                    showNavigation();

                    scrollAccumulator = 0;
                }
            }


            lastScrollY = currentScrollY;
        };


        window.addEventListener(
            'scroll',
            handleScroll,
            {
                passive: true
            }
        );


        /* --------------------------------------------------------
           RESIZE
           -------------------------------------------------------- */

        const resetHeader = () => {
            showNavigation();

            setMobileMenu(false);

            scrollAccumulator = 0;

            lastScrollY = Math.max(
                window.scrollY,
                0
            );
        };


        if (
            desktopNavigation.addEventListener
        ) {
            desktopNavigation.addEventListener(
                'change',
                resetHeader
            );
        } else {
            desktopNavigation.addListener(
                resetHeader
            );
        }
    }
});
