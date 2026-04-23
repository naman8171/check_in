/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PastWorkAutoSubmit = publicWidget.Widget.extend({
    selector: ".pw-filter-form",
    events: {
        "change select[name='category']": "_onCategoryChange",
    },

    _onCategoryChange() {
        this.el.submit();
    },
});
