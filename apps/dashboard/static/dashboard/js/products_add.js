/* ==========================================================================
   Panchakanya Collections
   Dashboard Add Product
   Dynamic Product Image Formset

   Namespace:
   pk-db-product-add-
   ========================================================================== */

(function () {
    "use strict";

    const container = document.getElementById(
        "pk-db-product-add-image-container"
    );

    const addButton = document.getElementById(
        "pk-db-product-add-image-button"
    );

    const template = document.getElementById(
        "pk-db-product-add-image-template"
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
