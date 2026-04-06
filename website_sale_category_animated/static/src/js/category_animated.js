/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedUI = publicWidget.Widget.extend({
    selector: "body",

    start() {
        this._initEnhancer();

        // 🔥 store observer (important fix)
        this._observer = this._observeChanges();

        return this._super(...arguments);
    },

    destroy() {
        // 🔥 cleanup (memory leak fix)
        if (this._observer) {
            this._observer.disconnect();
        }
        this._super(...arguments);
    },

    _initEnhancer() {
        setTimeout(() => {
            this._decorateAll();
        }, 500);
    },

    _decorateAll() {
        this._decorateSidebar();
        this._decorateTopCategories();
        this._decorateProducts();
    },

    /* ============================= */
    /* 🔥 SIDEBAR */
    /* ============================= */

_decorateSidebar() {
    const container = document.querySelector("#products_grid_before");
    if (!container) return;

    const cards = container.querySelectorAll("a");

    cards.forEach((card, index) => {

        // ✅ prevent duplicate binding
        if (card.dataset.enhanced) return;
        card.dataset.enhanced = "true";

        card.classList.remove("nav-link");
        card.classList.add("my_sidebar_cat");

        card.style.animationDelay = `${Math.min(index * 80, 600)}ms`;

        card.addEventListener("click", (e) => {

            // 🔥 better submenu detection
            let submenu = card.nextElementSibling;

            if (!submenu || submenu.tagName !== "UL") {
                submenu = card.closest("li")?.querySelector(":scope > ul");
            }

            // 👉 agar submenu nahi hai → normal redirect
            if (!submenu || submenu.tagName !== "UL") return;

            e.preventDefault();
            e.stopPropagation();

            const isOpen = submenu.classList.contains("open");

            // 🔥 CLOSE (same click)
            if (isOpen) {
                submenu.classList.remove("open");
                card.classList.remove("active");
                return;
            }

            // 🔥 CLOSE ALL (accordion behavior)
            container.querySelectorAll("ul.open").forEach(ul => {
                ul.classList.remove("open");
            });

            container.querySelectorAll("a.active").forEach(a => {
                a.classList.remove("active");
            });

            // 🔥 OPEN CURRENT
            submenu.classList.add("open");
            card.classList.add("active");
        });
    });
},

    /* ============================= */
    /* 🔹 TOP CATEGORIES */
    /* ============================= */

    _decorateTopCategories() {
        const cards = document.querySelectorAll(".o_wsale_categories_grid a");

        cards.forEach((card, index) => {
            if (card.classList.contains("my_top_cat")) return;

            card.classList.add("my_top_cat");
            card.style.animationDelay = `${Math.min(index * 100, 800)}ms`;
        });
    },

    /* ============================= */
    /* 🔹 PRODUCTS */
    /* ============================= */

    _decorateProducts() {
        const products = document.querySelectorAll(".oe_product");

        products.forEach((product, index) => {
            if (product.classList.contains("my_product_card")) return;

            product.classList.add("my_product_card");
            product.style.animationDelay = `${Math.min(index * 50, 500)}ms`;
        });
    },

    /* ============================= */
    /* 🔥 OBSERVER */
    /* ============================= */

    _observeChanges() {
        let timeout;

        const observer = new MutationObserver(() => {
            clearTimeout(timeout);

            timeout = setTimeout(() => {
                this._decorateAll();
            }, 100);
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });

        return observer; // 🔥 important
    },
});
