document.addEventListener('DOMContentLoaded', () => {
    const deleteForms = document.querySelectorAll(
        '[data-review-delete]'
    );

    if (!deleteForms.length) {
        return;
    }

    deleteForms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            const productName =
                form.dataset.productName || 'this product';

            const confirmed = window.confirm(
                `Are you sure you want to delete your review for "${productName}"?`
            );

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
