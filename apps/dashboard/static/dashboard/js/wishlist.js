document.addEventListener('DOMContentLoaded', () => {
    const removeButtons = document.querySelectorAll(
        '[data-wishlist-remove]'
    );

    if (!removeButtons.length) {
        return;
    }

    removeButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            const productName =
                button.dataset.productName || 'this item';

            const confirmed = window.confirm(
                `Remove "${productName}" from your wishlist?`
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
