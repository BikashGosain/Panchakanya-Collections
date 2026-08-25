   (function () {
       "use strict";

       document.addEventListener("DOMContentLoaded", function () {
           const headerRoot = document.getElementById("pk-js-header-root");
           const toggleBtn = document.getElementById("pk-js-mobile-toggle");
           const navBar = document.getElementById("pk-js-nav-bar");
           const userBtn = document.getElementById("pk-js-user-btn");
           const userDropdown = document.getElementById("pk-js-user-dropdown");
           let lastScrollY = window.scrollY;
           const hideThreshold = 40;

           if (toggleBtn && navBar) {
               toggleBtn.addEventListener("click", function () {
                   const isOpen = navBar.classList.toggle("pk-nav-mobile-open");
                   toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
               });
           }

           if (userBtn && userDropdown) {
               userBtn.addEventListener("click", function (event) {
                   event.stopPropagation();
                   userDropdown.classList.toggle("pk-dropdown-open");
               });

               document.addEventListener("click", function (event) {
                   if (!userDropdown.contains(event.target) && !userBtn.contains(event.target)) {
                       userDropdown.classList.remove("pk-dropdown-open");
                   }
               });
           }

           const syncHeaderNavVisibility = function () {
               if (!headerRoot) {
                   return;
               }

               if (window.innerWidth <= 991) {
                   headerRoot.classList.remove("pk-hdr-nav-hidden");
                   lastScrollY = window.scrollY;
                   return;
               }

               const currentScrollY = window.scrollY;
               const isScrollingDown = currentScrollY > lastScrollY;

               if (isScrollingDown && currentScrollY > hideThreshold) {
                   headerRoot.classList.add("pk-hdr-nav-hidden");
               } else {
                   headerRoot.classList.remove("pk-hdr-nav-hidden");
               }

               lastScrollY = currentScrollY;
           };

           window.addEventListener("scroll", syncHeaderNavVisibility, { passive: true });
           window.addEventListener("resize", syncHeaderNavVisibility);
           syncHeaderNavVisibility();
       });
   })();
