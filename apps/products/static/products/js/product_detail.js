(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        /* =========================================================
           CONFIGURATION
           ========================================================= */

        const DEFAULT_IMAGE =
            window.PRODUCT_DEFAULT_IMAGE || "";

        /* =========================================================
           GALLERY ELEMENTS
           ========================================================= */

        const wrapper =
            document.getElementById("productMainImageWrapper");

        const mainImage =
            document.getElementById("mainProductImage");

        const thumbnails =
            Array.from(
                document.querySelectorAll(".product-thumbnail")
            );

        const imageCounter =
            document.getElementById("productImageCounter");

        let currentIndex = 0;

        let lightbox = null;
        let lightboxImage = null;

        let touchStartX = 0;
        let touchStartY = 0;


        /* =========================================================
           GALLERY HELPERS
           ========================================================= */

        function getImageUrl(index) {
            if (!thumbnails.length) {
                return DEFAULT_IMAGE;
            }

            const thumbnail =
                thumbnails[index];

            return (
                thumbnail?.dataset?.imageUrl ||
                DEFAULT_IMAGE
            );
        }


        function updateCounter(index) {
            if (!imageCounter || !thumbnails.length) {
                return;
            }

            imageCounter.textContent =
                `${index + 1} / ${thumbnails.length}`;
        }


        function updateThumbnailState(index) {
            thumbnails.forEach(function (thumbnail, thumbnailIndex) {
                const isActive =
                    thumbnailIndex === index;

                thumbnail.classList.toggle(
                    "active",
                    isActive
                );

                thumbnail.setAttribute(
                    "aria-pressed",
                    String(isActive)
                );
            });
        }


        function scrollThumbnailIntoView(index) {
            const thumbnail =
                thumbnails[index];

            if (!thumbnail) {
                return;
            }

            thumbnail.scrollIntoView({
                behavior: "smooth",
                block: "nearest",
                inline: "center"
            });
        }


        /* =========================================================
           CREATE MAIN IMAGE IF PRIMARY IMAGE IS MISSING
           ========================================================= */

        function ensureMainImage() {
            if (!wrapper || !thumbnails.length) {
                return null;
            }

            let image =
                document.getElementById(
                    "mainProductImage"
                );

            if (image) {
                return image;
            }

            image =
                document.createElement("img");

            image.id =
                "mainProductImage";

            image.className =
                "product-main-image";

            image.alt =
                window.PRODUCT_NAME ||
                "Product image";

            image.draggable = false;

            wrapper.prepend(image);

            return image;
        }


        /* =========================================================
           SET MAIN IMAGE
           ========================================================= */

        function setMainImage(index, animate) {
            if (!thumbnails.length) {
                return;
            }

            const image =
                ensureMainImage();

            if (!image) {
                return;
            }

            const safeIndex =
                Math.max(
                    0,
                    Math.min(
                        index,
                        thumbnails.length - 1
                    )
                );

            const imageUrl =
                getImageUrl(safeIndex);

            currentIndex =
                safeIndex;

            image.onerror = function () {
                this.onerror = null;

                if (DEFAULT_IMAGE) {
                    this.src = DEFAULT_IMAGE;
                }
            };


            if (animate) {
                image.classList.add(
                    "is-changing"
                );

                window.setTimeout(
                    function () {
                        image.src =
                            imageUrl;

                        image.classList.remove(
                            "is-changing"
                        );
                    },
                    100
                );
            } else {
                image.src =
                    imageUrl;
            }


            updateThumbnailState(
                safeIndex
            );

            updateCounter(
                safeIndex
            );

            scrollThumbnailIntoView(
                safeIndex
            );
        }


        /* =========================================================
           INITIALIZE GALLERY
           ========================================================= */

        if (thumbnails.length) {

            let initialIndex = 0;

            const activeThumbnail =
                document.querySelector(
                    ".product-thumbnail.active"
                );

            if (activeThumbnail) {
                const parsedIndex =
                    Number(
                        activeThumbnail.dataset.index
                    );

                if (
                    Number.isInteger(parsedIndex) &&
                    parsedIndex >= 0 &&
                    parsedIndex < thumbnails.length
                ) {
                    initialIndex =
                        parsedIndex;
                }
            }

            setMainImage(
                initialIndex,
                false
            );


            /* =====================================================
               THUMBNAIL CLICK
               ===================================================== */

            thumbnails.forEach(
                function (thumbnail, index) {

                    thumbnail.addEventListener(
                        "click",
                        function () {
                            setMainImage(
                                index,
                                true
                            );
                        }
                    );

                }
            );
        }


        /* =========================================================
           CREATE GALLERY ARROWS
           ========================================================= */

        function createGalleryArrow(
            direction,
            symbol,
            label
        ) {
            if (
                !wrapper ||
                thumbnails.length <= 1
            ) {
                return null;
            }

            const button =
                document.createElement(
                    "button"
                );

            button.type =
                "button";

            button.className =
                `product-gallery-arrow ${direction}`;

            button.innerHTML =
                symbol;

            button.setAttribute(
                "aria-label",
                label
            );

            wrapper.appendChild(
                button
            );

            return button;
        }


        const previousButton =
            createGalleryArrow(
                "prev",
                "&#8249;",
                "Previous product image"
            );

        const nextButton =
            createGalleryArrow(
                "next",
                "&#8250;",
                "Next product image"
            );


        function showPreviousImage() {
            if (!thumbnails.length) {
                return;
            }

            const previousIndex =
                currentIndex <= 0
                    ? thumbnails.length - 1
                    : currentIndex - 1;

            setMainImage(
                previousIndex,
                true
            );
        }


        function showNextImage() {
            if (!thumbnails.length) {
                return;
            }

            const nextIndex =
                currentIndex >= thumbnails.length - 1
                    ? 0
                    : currentIndex + 1;

            setMainImage(
                nextIndex,
                true
            );
        }


        if (previousButton) {
            previousButton.addEventListener(
                "click",
                showPreviousImage
            );
        }

        if (nextButton) {
            nextButton.addEventListener(
                "click",
                showNextImage
            );
        }


        /* =========================================================
           KEYBOARD NAVIGATION
           ========================================================= */

        document.addEventListener(
            "keydown",
            function (event) {

                /*
                 * Don't hijack arrow keys while typing.
                 */

                const activeElement =
                    document.activeElement;

                const isTyping =
                    activeElement &&
                    (
                        activeElement.tagName === "INPUT" ||
                        activeElement.tagName === "TEXTAREA" ||
                        activeElement.tagName === "SELECT"
                    );

                if (isTyping) {
                    return;
                }


                if (event.key === "ArrowLeft") {
                    showPreviousImage();
                }


                if (event.key === "ArrowRight") {
                    showNextImage();
                }

            }
        );


        /* =========================================================
           TOUCH SWIPE
           ========================================================= */

        if (wrapper && thumbnails.length > 1) {

            wrapper.addEventListener(
                "touchstart",
                function (event) {

                    const touch =
                        event.changedTouches[0];

                    touchStartX =
                        touch.clientX;

                    touchStartY =
                        touch.clientY;

                },
                {
                    passive: true
                }
            );


            wrapper.addEventListener(
                "touchend",
                function (event) {

                    const touch =
                        event.changedTouches[0];

                    const deltaX =
                        touch.clientX -
                        touchStartX;

                    const deltaY =
                        touch.clientY -
                        touchStartY;


                    /*
                     * Ignore mostly vertical gestures.
                     */

                    if (
                        Math.abs(deltaX) <
                        45
                    ) {
                        return;
                    }

                    if (
                        Math.abs(deltaX) <
                        Math.abs(deltaY)
                    ) {
                        return;
                    }


                    if (deltaX < 0) {
                        showNextImage();
                    } else {
                        showPreviousImage();
                    }

                },
                {
                    passive: true
                }
            );
        }


        /* =========================================================
           LIGHTBOX
           ========================================================= */

        function createLightbox() {

            if (lightbox) {
                return;
            }

            lightbox =
                document.createElement(
                    "div"
                );

            lightbox.className =
                "product-lightbox";

            lightbox.setAttribute(
                "role",
                "dialog"
            );

            lightbox.setAttribute(
                "aria-modal",
                "true"
            );

            lightbox.setAttribute(
                "aria-label",
                "Product image viewer"
            );


            lightbox.innerHTML = `
                <button
                    type="button"
                    class="product-lightbox-close"
                    aria-label="Close image viewer"
                >
                    ×
                </button>

                <button
                    type="button"
                    class="product-lightbox-prev"
                    aria-label="Previous image"
                >
                    ‹
                </button>

                <img
                    class="product-lightbox-image"
                    alt=""
                >

                <button
                    type="button"
                    class="product-lightbox-next"
                    aria-label="Next image"
                >
                    ›
                </button>
            `;


            document.body.appendChild(
                lightbox
            );


            lightboxImage =
                lightbox.querySelector(
                    ".product-lightbox-image"
                );


            const closeButton =
                lightbox.querySelector(
                    ".product-lightbox-close"
                );

            const previousButton =
                lightbox.querySelector(
                    ".product-lightbox-prev"
                );

            const nextButton =
                lightbox.querySelector(
                    ".product-lightbox-next"
                );


            closeButton.addEventListener(
                "click",
                closeLightbox
            );

            previousButton.addEventListener(
                "click",
                function () {
                    showPreviousImage();

                    updateLightboxImage();
                }
            );

            nextButton.addEventListener(
                "click",
                function () {
                    showNextImage();

                    updateLightboxImage();
                }
            );


            /*
             * Clicking the dark background closes
             * the viewer.
             */

            lightbox.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target === lightbox
                    ) {
                        closeLightbox();
                    }

                }
            );
        }


        function updateLightboxImage() {

            if (
                !lightboxImage ||
                !thumbnails.length
            ) {
                return;
            }

            lightboxImage.src =
                getImageUrl(
                    currentIndex
                );

            lightboxImage.alt =
                window.PRODUCT_NAME ||
                "Product image";
        }


        function openLightbox() {

            if (
                !wrapper ||
                !thumbnails.length
            ) {
                return;
            }

            createLightbox();

            updateLightboxImage();

            lightbox.classList.add(
                "is-open"
            );

            document.body.style.overflow =
                "hidden";


            const closeButton =
                lightbox.querySelector(
                    ".product-lightbox-close"
                );

            if (closeButton) {
                closeButton.focus();
            }
        }


        function closeLightbox() {

            if (!lightbox) {
                return;
            }

            lightbox.classList.remove(
                "is-open"
            );

            document.body.style.overflow =
                "";
        }


        if (wrapper && thumbnails.length) {

            wrapper.addEventListener(
                "click",
                function (event) {

                    /*
                     * Don't open lightbox when
                     * clicking navigation buttons.
                     */

                    if (
                        event.target.closest(
                            ".product-gallery-arrow"
                        )
                    ) {
                        return;
                    }

                    openLightbox();

                }
            );

        }


        /* =========================================================
           LIGHTBOX KEYBOARD CONTROL
           ========================================================= */

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    !lightbox ||
                    !lightbox.classList.contains(
                        "is-open"
                    )
                ) {
                    return;
                }


                if (event.key === "Escape") {
                    closeLightbox();
                }


                if (event.key === "ArrowLeft") {
                    showPreviousImage();

                    updateLightboxImage();
                }


                if (event.key === "ArrowRight") {
                    showNextImage();

                    updateLightboxImage();
                }

            }
        );


        /* =========================================================
           QUANTITY
           ========================================================= */

        const quantityValue =
            document.getElementById(
                "quantityValue"
            );

        const cartQuantity =
            document.getElementById(
                "cartQuantity"
            );

        const decreaseButton =
            document.getElementById(
                "decreaseQuantity"
            );

        const increaseButton =
            document.getElementById(
                "increaseQuantity"
            );


        if (
            quantityValue &&
            cartQuantity &&
            decreaseButton &&
            increaseButton
        ) {

            let quantity = 1;

            const stock =
                Math.max(
                    0,
                    Number(
                        increaseButton.dataset.stock
                    ) || 0
                );


            function updateQuantity(
                newQuantity
            ) {

                quantity =
                    Math.max(
                        1,
                        Math.min(
                            newQuantity,
                            stock || 1
                        )
                    );


                quantityValue.textContent =
                    String(quantity);

                cartQuantity.value =
                    String(quantity);


                decreaseButton.disabled =
                    quantity <= 1;


                increaseButton.disabled =
                    stock <= 0 ||
                    quantity >= stock;
            }


            decreaseButton.addEventListener(
                "click",
                function () {

                    if (quantity > 1) {
                        updateQuantity(
                            quantity - 1
                        );
                    }

                }
            );


            increaseButton.addEventListener(
                "click",
                function () {

                    if (
                        stock > 0 &&
                        quantity < stock
                    ) {
                        updateQuantity(
                            quantity + 1
                        );
                    }

                }
            );


            updateQuantity(1);
        }


        /* =========================================================
           WISHLIST BUTTON LOADING STATE
           ========================================================= */

        const wishlistForms =
            document.querySelectorAll(
                'form[action*="wishlists"]'
            );


        wishlistForms.forEach(
            function (form) {

                form.addEventListener(
                    "submit",
                    function () {

                        const button =
                            form.querySelector(
                                "button"
                            );

                        if (!button) {
                            return;
                        }

                        button.disabled =
                            true;

                        button.style.opacity =
                            "0.65";

                    }
                );

            }
        );

    });
})();
