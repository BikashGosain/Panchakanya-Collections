/* ==========================================================================
   Panchakanya Collections
   Dashboard Edit Product
   Dynamic Product Image Formset

   Namespace:
   pk-db-product-edit-
   ========================================================================== */

(function () {
    "use strict";

    const container = document.getElementById(
        "pk-db-product-edit-image-container"
    );

    const addButton = document.getElementById(
        "pk-db-product-edit-image-button"
    );

    const template = document.getElementById(
        "pk-db-product-edit-image-template"
    );

    if (!container || !addButton || !template) {
        return;
    }


    const totalFormsInput = document.querySelector(
        'input[name$="-TOTAL_FORMS"]'
    );

    if (!totalFormsInput) {
        return;
    }


    addButton.addEventListener("click", function () {

        const currentFormCount = Number(totalFormsInput.value);

        const templateHtml = template.innerHTML.replace(
            /__prefix__/g,
            currentFormCount
        );

        container.insertAdjacentHTML(
            "beforeend",
            templateHtml
        );

        totalFormsInput.value = currentFormCount + 1;

    });

})();
