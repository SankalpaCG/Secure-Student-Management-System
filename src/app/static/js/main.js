/**
 * Secure Student MS — UI interactions
 */
(function () {
    "use strict";

    // Sidebar toggle (mobile)
    const sidebar = document.getElementById("appSidebar");
    const backdrop = document.getElementById("sidebarBackdrop");
    const toggleBtn = document.getElementById("sidebarToggle");

    function closeSidebar() {
        sidebar?.classList.remove("show");
        backdrop?.classList.remove("show");
    }

    function openSidebar() {
        sidebar?.classList.add("show");
        backdrop?.classList.add("show");
    }

    toggleBtn?.addEventListener("click", () => {
        if (sidebar?.classList.contains("show")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    backdrop?.addEventListener("click", closeSidebar);

    // Searchable tables
    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const targetSelector = input.getAttribute("data-table-target");
        const table = targetSelector
            ? document.querySelector(targetSelector)
            : input.closest(".card-app, .table-responsive")?.querySelector("table");

        if (!table) return;

        input.addEventListener("input", () => {
            const query = input.value.toLowerCase().trim();
            table.querySelectorAll("tbody tr").forEach((row) => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? "" : "none";
            });
        });
    });

    // Auto-dismiss flash alerts after 6s
    document.querySelectorAll(".flash-alert").forEach((alert) => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });
})();
