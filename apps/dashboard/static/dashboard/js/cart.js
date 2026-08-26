document.addEventListener('DOMContentLoaded', () => {
    const removeButtons = document.querySelectorAll(
        '[data-cart-remove]'
    );

    removeButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            const productName =
                button.dataset.productName || 'this item';

            const confirmed = window.confirm(
                `Remove "${productName}" from your cart?`
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
