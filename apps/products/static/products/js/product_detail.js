(function () {
    "use strict";

    const DEFAULT_IMAGE = window.PRODUCT_DEFAULT_IMAGE || "";

    document.addEventListener("DOMContentLoaded", function () {
        /* ============ GALLERY ============ */
        const mainImage = document.getElementById("mainProductImage");
        const thumbnails = document.querySelectorAll(".product-thumbnail");
        const imageCounter = document.getElementById("productImageCounter");

        function updateImageCounter(index) {
            if (imageCounter) imageCounter.textContent = `${index + 1} / ${thumbnails.length}`;
        }

        function setMainImage(imageUrl, thumbnail, index) {
            if (!mainImage || !imageUrl) return;
            mainImage.onerror = function () {
                this.onerror = null;
                if (DEFAULT_IMAGE) this.src = DEFAULT_IMAGE;
            };
            mainImage.src = imageUrl;
            thumbnails.forEach((btn) => btn.classList.remove("active"));
            if (thumbnail) thumbnail.classList.add("active");
            updateImageCounter(index);
        }

        thumbnails.forEach((thumbnail, index) => {
            thumbnail.addEventListener("click", function () {
                setMainImage(this.dataset.imageUrl, this, index);
            });
        });

        if (thumbnails.length) {
            let active = document.querySelector(".product-thumbnail.active") || thumbnails[0];
            active.classList.add("active");
            updateImageCounter(Number(active.dataset.index));
        }

        /* ============ QUANTITY ============ */
        const quantityValue = document.getElementById("quantityValue");
        const cartQuantity = document.getElementById("cartQuantity");
        const decreaseButton = document.getElementById("decreaseQuantity");
        const increaseButton = document.getElementById("increaseQuantity");

        if (quantityValue && cartQuantity && decreaseButton && increaseButton) {
            let quantity = 1;
            const stock = Number(increaseButton.dataset.stock);

            function updateQuantity(value) {
                quantity = value;
                quantityValue.textContent = String(quantity);
                cartQuantity.value = String(quantity);
                decreaseButton.disabled = quantity <= 1;
                increaseButton.disabled = stock <= 0 || quantity >= stock;
            }

            decreaseButton.addEventListener("click", () => {
                if (quantity > 1) updateQuantity(quantity - 1);
            });
            increaseButton.addEventListener("click", () => {
                if (quantity < stock) updateQuantity(quantity + 1);
            });

            updateQuantity(1);
        }

        /* ============ KEYBOARD NAV ============ */
        document.addEventListener("keydown", function (event) {
            if (!thumbnails.length) return;
            const activeIndex = Array.from(thumbnails).findIndex((t) => t.classList.contains("active"));
            if (event.key === "ArrowRight") {
                const next = Math.min(activeIndex + 1, thumbnails.length - 1);
                if (next !== activeIndex) setMainImage(thumbnails[next].dataset.imageUrl, thumbnails[next], next);
            }
            if (event.key === "ArrowLeft") {
                const prev = Math.max(activeIndex - 1, 0);
                if (prev !== activeIndex) setMainImage(thumbnails[prev].dataset.imageUrl, thumbnails[prev], prev);
            }
        });
    });
})();
