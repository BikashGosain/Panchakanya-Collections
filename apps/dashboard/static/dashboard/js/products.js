document.addEventListener('DOMContentLoaded', () => {
    const actionForms = document.querySelectorAll(
        '[data-product-action]'
    );

    if (!actionForms.length) {
        return;
    }

    actionForms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            const action = form.dataset.productAction;
            const productName =
                form.dataset.productName || 'this product';

            let message;

            if (action === 'delete') {
                message =
                    `Are you sure you want to delete "${productName}"?`;
            } else if (action === 'restore') {
                message =
                    `Restore "${productName}"?`;
            } else {
                return;
            }

            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
});
