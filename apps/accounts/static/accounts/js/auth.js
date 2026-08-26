(function () {
    "use strict";

    const root = document.querySelector(".pk-auth-root");
    if (!root) return;

    const primaryForm = root.querySelector(".pk-auth-form");
    const submitBtn = primaryForm ? primaryForm.querySelector(".pk-auth-btn-primary") : null;

    if (primaryForm && submitBtn) {
        primaryForm.addEventListener("submit", function () {
            submitBtn.disabled = true;
            submitBtn.textContent = submitBtn.dataset.loadingText || "Please wait...";
        });
    }
})();
