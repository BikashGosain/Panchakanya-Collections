document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.getElementById("add-image-form");
    const container = document.getElementById("image-formset-container");
    const templateEl = document.getElementById("image-form-template");
    const totalFormsInput = document.querySelector("#id_images-TOTAL_FORMS");

    if (!addButton || !container || !templateEl || !totalFormsInput) return;

    addButton.addEventListener("click", function () {
        const formCount = parseInt(totalFormsInput.value, 10);
        const templateHtml = templateEl.innerHTML.replace(/__prefix__/g, formCount);

        const wrapper = document.createElement("div");
        wrapper.innerHTML = templateHtml;
        container.appendChild(wrapper.firstElementChild);

        totalFormsInput.value = formCount + 1;
    });
});
