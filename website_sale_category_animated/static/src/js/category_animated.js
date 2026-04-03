/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedUI = publicWidget.Widget.extend({
    selector: "body",

    start() {
        this._initEnhancer();
        this._observeChanges();
        return this._super(...arguments);
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

    // 🔥 SIDEBAR FINAL WORKING
    _decorateSidebar() {
        const cards = document.querySelectorAll("#products_grid_before a");

        cards.forEach((card, index) => {

            // ✅ prevent duplicate binding
            if (card.dataset.enhanced) return;
            card.dataset.enhanced = "true";

            // remove Odoo class
            card.classList.remove("nav-link");

            // add custom class
            card.classList.add("my_sidebar_cat");

            // animation delay
            card.style.animationDelay = `${Math.min(index * 80, 600)}ms`;

            // 🔥 CLICK TOGGLE (FINAL FIX)
            card.addEventListener("click", (e) => {
                let submenu = card.nextElementSibling;

                // fallback for different DOM structure
                if (!submenu || submenu.tagName !== "UL") {
                    submenu = card.parentElement.querySelector("ul");
                }

                // normal redirect if no submenu
                if (!submenu || submenu.tagName !== "UL") return;

                e.preventDefault();
                e.stopPropagation();

                const isOpen = submenu.classList.contains("open");

                if (isOpen) {
                    submenu.classList.remove("open");
                    card.classList.remove("active");
                    return;
                }

                // ✅ ACCORDION: close other submenus
                document.querySelectorAll("#products_grid_before ul.open").forEach(ul => {
                    if (ul !== submenu) ul.classList.remove("open");
                });

                document.querySelectorAll("#products_grid_before a.active").forEach(a => {
                    if (a !== card) a.classList.remove("active");
                });

                // ✅ OPEN current submenu
                submenu.classList.add("open");
                card.classList.add("active");
            });
        });
    },

    // 🔹 Top categories
    _decorateTopCategories() {
        const cards = document.querySelectorAll(".o_wsale_categories_grid a");

        cards.forEach((card, index) => {
            if (!card.classList.contains("my_top_cat")) {
                card.classList.add("my_top_cat");
                card.style.animationDelay = `${Math.min(index * 100, 800)}ms`;
            }
        });
    },

    // 🔹 Products
    _decorateProducts() {
        const products = document.querySelectorAll(".oe_product");

        products.forEach((product, index) => {
            if (!product.classList.contains("my_product_card")) {
                product.classList.add("my_product_card");
                product.style.animationDelay = `${Math.min(index * 50, 500)}ms`;
            }
        });
    },

    // 🔥 Observe DOM safely with debounce
    _observeChanges() {
        let timeout;
        const observer = new MutationObserver(() => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this._decorateAll(), 100); // debounce 100ms
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    },
});