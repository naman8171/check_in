/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedCategories = publicWidget.Widget.extend({
    selector: ".oe_website_sale",

    events: {
        "click .o_wsale_products_categories [data-bs-toggle='collapse']": "_onCategoryToggleClick",
        "click .o_wsale_products_categories_list [data-bs-toggle='collapse']": "_onCategoryToggleClick",
    },

    start() {
        this._decorateCategories();
        return this._super(...arguments);
    },

    _decorateCategories() {
        const selectors = [
            ".o_wsale_products_categories a",
            ".o_wsale_products_categories_list a",
        ];

        const cards = this.el.querySelectorAll(selectors.join(","));
        cards.forEach((card, index) => {
            card.classList.add("o_cat_card");
            card.style.animationDelay = `${Math.min(index * 55, 500)}ms`;
        });
    },

    _onCategoryToggleClick(ev) {
        const toggle = ev.currentTarget;
        const targetSelector = toggle.dataset.bsTarget || toggle.getAttribute("href");

        if (!targetSelector || !targetSelector.startsWith("#")) {
            return;
        }

        const target = this.el.querySelector(targetSelector);
        if (!target) {
            return;
        }

        ev.preventDefault();

        if (target.classList.contains("show")) {
            target.classList.remove("show");
            toggle.classList.add("collapsed");
            toggle.setAttribute("aria-expanded", "false");
        } else {
            target.classList.add("show");
            toggle.classList.remove("collapsed");
            toggle.setAttribute("aria-expanded", "true");
        }
    },
});
