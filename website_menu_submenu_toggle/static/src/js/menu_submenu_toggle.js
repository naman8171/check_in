/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteMenuSubmenuToggle = publicWidget.Widget.extend({
    selector: "body",

    start() {
        this._domObserver = this._observeChanges();
        this._decorateMenus();
        return this._super(...arguments);
    },

    destroy() {
        if (this._domObserver) {
            this._domObserver.disconnect();
        }
        this._super(...arguments);
    },

    _decorateMenus() {
        document.querySelectorAll("header .dropdown, #top_menu .dropdown").forEach((menu) => {
            const trigger =
                menu.querySelector(":scope > a.dropdown-toggle") ||
                menu.querySelector(":scope > a, :scope > button.dropdown-toggle");
            const submenu = menu.querySelector(":scope > .dropdown-menu");

            if (!trigger || !submenu || trigger.dataset.wmstBound === "true") {
                return;
            }

            trigger.dataset.wmstBound = "true";
            trigger.setAttribute("aria-expanded", menu.classList.contains("show") ? "true" : "false");

            trigger.addEventListener("click", (event) => this._onMenuClick(event, menu, trigger, submenu));
            trigger.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    this._onMenuClick(event, menu, trigger, submenu);
                }
            });
        });
    },

    _onMenuClick(event, menu, trigger, submenu) {
        event.preventDefault();
        event.stopPropagation();

        const shouldOpen = !(menu.classList.contains("show") || submenu.classList.contains("show"));
        const menuRoot = menu.closest("#top_menu, .navbar, header") || document;

        menuRoot.querySelectorAll(".dropdown.show").forEach((openMenu) => {
            if (openMenu !== menu) {
                this._setMenuState(openMenu, false);
            }
        });

        this._setMenuState(menu, shouldOpen, trigger, submenu);
    },

    _setMenuState(menu, shouldOpen, trigger = null, submenu = null) {
        const menuTrigger =
            trigger ||
            menu.querySelector(":scope > a.dropdown-toggle, :scope > a, :scope > button.dropdown-toggle");
        const menuSubmenu = submenu || menu.querySelector(":scope > .dropdown-menu");

        if (!menuTrigger || !menuSubmenu) {
            return;
        }

        menu.classList.toggle("show", shouldOpen);
        menuSubmenu.classList.toggle("show", shouldOpen);
        menuTrigger.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
    },

    _observeChanges() {
        let timeout;
        const observer = new MutationObserver(() => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this._decorateMenus(), 120);
        });

        observer.observe(document.body, { childList: true, subtree: true });
        return observer;
    },
});
