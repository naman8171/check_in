/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedCategories = publicWidget.Widget.extend({
    selector: ".oe_website_sale",

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
});
