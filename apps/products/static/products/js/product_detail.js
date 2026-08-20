/* =========================================================
   PANCHAKANYA COLLECTIONS
   PRODUCT DETAIL PAGE
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIGURATION
       ===================================================== */

    const DEFAULT_IMAGE =
        window.PRODUCT_DEFAULT_IMAGE || "";


    /* =====================================================
       DOM ELEMENTS
       ===================================================== */

    const mainImage =
        document.getElementById("mainProductImage");

    const thumbnails =
        document.querySelectorAll(".product-thumbnail");

    const imageCounter =
        document.getElementById("productImageCounter");

    const quantityValue =
        document.getElementById("quantityValue");

    const decreaseQuantityButton =
        document.getElementById("decreaseQuantity");

    const increaseQuantityButton =
        document.getElementById("increaseQuantity");

    const addToCartButton =
        document.getElementById("addToCartButton");


    /* =====================================================
       IMAGE GALLERY
       ===================================================== */

    function updateImageCounter(index) {

        if (!imageCounter) {
            return;
        }

        imageCounter.textContent =
            `${index + 1} / ${thumbnails.length}`;
    }


    function setMainImage(imageUrl, thumbnail, index) {

        if (!mainImage || !imageUrl) {
            return;
        }


        /*
         * Small fade effect while changing image.
         */

        mainImage.classList.add("is-changing");


        /*
         * Remove previous error handler.
         */

        mainImage.onerror = null;


        /*
         * Handle broken product image.
         */

        mainImage.onerror = function () {

            this.onerror = null;

            if (DEFAULT_IMAGE) {
                this.src = DEFAULT_IMAGE;
            }

            this.classList.remove(
                "is-changing"
            );
        };


        /*
         * Load selected image.
         */

        mainImage.src = imageUrl;


        mainImage.onload = function () {

            this.classList.remove(
                "is-changing"
            );
        };


        /*
         * Update active thumbnail.
         */

        thumbnails.forEach(function (button) {

            button.classList.remove("active");

        });


        if (thumbnail) {

            thumbnail.classList.add("active");

        }


        /*
         * Update image counter.
         */

        updateImageCounter(index);
    }


    function initializeGallery() {

        if (!thumbnails.length) {
            return;
        }


        /*
         * Find primary/active thumbnail.
         */

        let activeThumbnail =
            document.querySelector(
                ".product-thumbnail.active"
            );


        /*
         * If no primary image exists,
         * use the first image.
         */

        if (!activeThumbnail) {

            activeThumbnail =
                thumbnails[0];

            activeThumbnail.classList.add(
                "active"
            );
        }


        const imageUrl =
            activeThumbnail.dataset.imageUrl;

        const imageIndex =
            Number(
                activeThumbnail.dataset.index
            );


        /*
         * If the main image does not exist,
         * create it from the first/primary image.
         */

        if (!mainImage) {

            const imageWrapper =
                document.getElementById(
                    "productMainImageWrapper"
                );


            if (!imageWrapper) {
                return;
            }


            const newImage =
                document.createElement("img");


            newImage.id =
                "mainProductImage";

            newImage.className =
                "product-main-image";

            newImage.alt =
                window.PRODUCT_NAME || "Product";


            newImage.src =
                imageUrl;


            newImage.onerror =
                function () {

                    this.onerror = null;

                    if (DEFAULT_IMAGE) {
                        this.src = DEFAULT_IMAGE;
                    }

                };


            imageWrapper.prepend(
                newImage
            );

        }


        /*
         * Update initial counter.
         */

        updateImageCounter(
            imageIndex
        );
    }


    /*
     * Thumbnail click events.
     */

    thumbnails.forEach(function (thumbnail, index) {

        thumbnail.addEventListener(
            "click",
            function () {

                const imageUrl =
                    this.dataset.imageUrl;


                setMainImage(
                    imageUrl,
                    this,
                    index
                );

            }
        );

    });


    /* =====================================================
       QUANTITY
       ===================================================== */

    let quantity = 1;


    function updateQuantity() {

        if (!quantityValue) {
            return;
        }

        quantityValue.textContent =
            quantity;

        if (decreaseQuantityButton) {

            decreaseQuantityButton.disabled =
                quantity <= 1;

        }
    }


    if (decreaseQuantityButton) {

        decreaseQuantityButton.addEventListener(
            "click",
            function () {

                if (quantity > 1) {

                    quantity--;

                    updateQuantity();

                }

            }
        );
    }


    if (increaseQuantityButton) {

        increaseQuantityButton.addEventListener(
            "click",
            function () {

                const maxStock =
                    Number(
                        this.dataset.stock
                    );


                if (
                    maxStock > 0 &&
                    quantity < maxStock
                ) {

                    quantity++;

                    updateQuantity();

                }

            }
        );
    }


    /* =====================================================
       ADD TO CART
       ===================================================== */

    if (addToCartButton) {

        addToCartButton.addEventListener(
            "click",
            function () {

                /*
                 * Cart functionality can be connected
                 * here when the cart URL/form is ready.
                 */

                const productId =
                    this.dataset.productId;


                const selectedQuantity =
                    quantity;


                console.log(
                    "Add to cart:",
                    {
                        productId:
                            productId,

                        quantity:
                            selectedQuantity
                    }
                );

            }
        );
    }


    /* =====================================================
       KEYBOARD GALLERY NAVIGATION
       ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (!thumbnails.length) {
                return;
            }


            const activeIndex =
                Array.from(thumbnails)
                    .findIndex(
                        function (thumbnail) {
                            return thumbnail.classList.contains(
                                "active"
                            );
                        }
                    );


            if (event.key === "ArrowRight") {

                const nextIndex =
                    Math.min(
                        activeIndex + 1,
                        thumbnails.length - 1
                    );


                if (nextIndex !== activeIndex) {

                    const nextThumbnail =
                        thumbnails[nextIndex];

                    setMainImage(
                        nextThumbnail.dataset.imageUrl,
                        nextThumbnail,
                        nextIndex
                    );

                }
            }


            if (event.key === "ArrowLeft") {

                const previousIndex =
                    Math.max(
                        activeIndex - 1,
                        0
                    );


                if (
                    previousIndex !==
                    activeIndex
                ) {

                    const previousThumbnail =
                        thumbnails[previousIndex];

                    setMainImage(
                        previousThumbnail.dataset.imageUrl,
                        previousThumbnail,
                        previousIndex
                    );

                }
            }

        }
    );


    /* =====================================================
       INITIALIZE
       ===================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initializeGallery();

            updateQuantity();

        }
    );

})();
