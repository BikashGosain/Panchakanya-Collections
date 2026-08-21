(function () {
    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? match[2] : null;
    }

    function attachLikeHandlers(container) {
        container.querySelectorAll(".rv-like-form").forEach((form) => {
            form.addEventListener("submit", async function (e) {
                e.preventDefault();
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                });
                if (response.redirected || response.ok) {
                    window.location.reload();
                }
            });
        });
    }

    function initShowMore() {
        const btn = document.getElementById("rv-show-more");
        if (!btn) return;

        btn.addEventListener("click", async function () {
            const productId = btn.dataset.productId;
            const offset = btn.dataset.offset;
            const sort = btn.dataset.sort;

            btn.textContent = "Loading...";
            btn.disabled = true;

            const url = `/reviews/load-more/${productId}/?offset=${offset}&sort=${sort}`;
            const response = await fetch(url);
            const html = await response.text();

            const list = document.getElementById("rv-items-list");
            const temp = document.createElement("div");
            temp.innerHTML = html;
            Array.from(temp.children).forEach((child) => list.appendChild(child));

            attachLikeHandlers(list);

            // Ask the server (via a hidden marker) whether more remain — simplest: re-check by another attribute
            const hasMoreMarker = temp.querySelector("[data-has-more]");
            btn.textContent = "Show More";
            btn.disabled = false;
            btn.dataset.offset = parseInt(offset) + 5;
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        const scrollArea = document.getElementById("rv-scroll-area");
        if (scrollArea) attachLikeHandlers(scrollArea);
        initShowMore();
    });
})();
