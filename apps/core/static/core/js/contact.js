<script>
    document.addEventListener("DOMContentLoaded", function () {
        const form = document.getElementById("pk-contact-form");
        const button = document.getElementById("pk-contact-submit");
        const status = document.getElementById("pk-contact-status");

        if (!form || !button || !status) {
            return;
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            button.disabled = true;
            button.innerHTML = 'Sending...';

            status.hidden = true;
            status.textContent = "";

            const formData = new FormData(form);

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "Accept": "application/json"
                    }
                });

                if (response.ok) {
                    form.reset();

                    status.textContent =
                        "Thank you for contacting us. Your enquiry has been sent successfully. We will get back to you soon.";

                    status.hidden = false;
                    status.classList.add("pk-contact-status-success");
                } else {
                    throw new Error("Form submission failed.");
                }
            } catch (error) {
                status.textContent =
                    "Sorry, we couldn't send your message right now. Please try again later.";

                status.hidden = false;
                status.classList.add("pk-contact-status-error");
            } finally {
                button.disabled = false;
                button.innerHTML = 'Send Message <span aria-hidden="true">→</span>';
            }
        });
    });
</script>
