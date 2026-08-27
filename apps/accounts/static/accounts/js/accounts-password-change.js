document.querySelector(".pk-password-change-actions button")
    .closest("form")
    .addEventListener("submit", function () {
        const button = this.querySelector("button[type='submit']");

        button.textContent = "Changing Password...";
        button.disabled = true;
    });
