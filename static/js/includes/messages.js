/* ==========================================================================
   Panchakanya Collections
   Global Django Messages

   Namespace:
   pk-msg-

   Handles:
   - Manual close
   - Automatic dismissal
   ========================================================================== */

(function () {
    "use strict";

    const messages = document.querySelectorAll(".pk-msg");

    if (!messages.length) {
        return;
    }


    messages.forEach(function (message) {

        const closeButton = message.querySelector(
            ".pk-msg-close"
        );

        function closeMessage() {

            if (message.classList.contains("pk-msg--closing")) {
                return;
            }

            message.classList.add("pk-msg--closing");

            message.addEventListener(
                "animationend",
                function () {
                    message.remove();
                },
                { once: true }
            );

        }


        if (closeButton) {
            closeButton.addEventListener(
                "click",
                closeMessage
            );
        }


        /*
         * Automatically dismiss messages after 5 seconds.
         *
         * Error messages stay visible until manually closed.
         */
        if (
            !message.classList.contains("pk-msg--error") &&
            !message.classList.contains("pk-msg--danger")
        ) {
            window.setTimeout(closeMessage, 5000);
        }

    });

})();
