/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedUI = publicWidget.Widget.extend({
    selector: "body",

    start() {
        this._domObserver = this._observeChanges();
        this._decorateAll();
        return this._super(...arguments);
    },

    destroy() {
        if (this._domObserver) {
            this._domObserver.disconnect();
        }
        this._super(...arguments);
    },

    _decorateAll() {
        this._decorateSidebar();
        this._decorateTopCategories();
        this._decorateProducts();
    },

    _decorateSidebar() {
        const container = document.querySelector("#products_grid_before");
        if (!container) return;

        const links = container.querySelectorAll("a");
        links.forEach((link) => {
            if (link.dataset.wscaEnhanced !== "true") {
                link.dataset.wscaEnhanced = "true";
                link.classList.remove("nav-link");
                link.classList.add("my_sidebar_cat");
            }

            const submenu = this._getSubmenu(link);
            if (!submenu) {
                link.classList.remove("has-submenu");
                return;
            }

            link.classList.add("has-submenu");
            submenu.dataset.wscaSubmenu = "true";
            if (link.dataset.wscaToggleBound !== "true") {
                link.dataset.wscaToggleBound = "true";
                link.setAttribute("role", "button");
                link.setAttribute("aria-expanded", "false");
                link.addEventListener("click", (ev) => this._onSidebarClick(ev, container, link, submenu));
                link.addEventListener("keydown", (ev) => {
                    if (ev.key === "Enter" || ev.key === " ") {
                        this._onSidebarClick(ev, container, link, submenu);
                    }
                });
            }

            if (this._isCurrentUrl(link.href)) {
                this._openAncestorMenus(link);
            }
        });
    },

    _getSubmenu(link) {
        const listItem = link.closest("li");
        if (!listItem) return null;
        return Array.from(listItem.children).find((el) => el.tagName === "UL" || el.classList.contains("collapse")) || null;
    },

    _setSubmenuState(link, submenu, shouldOpen) {
        submenu.classList.toggle("open", shouldOpen);
        submenu.classList.toggle("show", shouldOpen);
        link.classList.toggle("active", shouldOpen);
        link.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
    },

    _onSidebarClick(event, container, link, submenu) {
        event.preventDefault();
        event.stopPropagation();

        const isOpen = submenu.classList.contains("open");

        container.querySelectorAll("[data-wsca-submenu='true']").forEach((sub) => {
            if (sub !== submenu) {
                sub.classList.remove("open", "show");
                const ownerLink = sub.parentElement?.querySelector(":scope > a");
                if (ownerLink) {
                    ownerLink.classList.remove("active");
                    ownerLink.setAttribute("aria-expanded", "false");
                }
            }
        });

        this._setSubmenuState(link, submenu, !isOpen);
    },

    _openAncestorMenus(link) {
        let current = link.closest("li");
        while (current) {
            const currentLink = current.querySelector(":scope > a");
            const submenu = current.querySelector(":scope > ul");
            if (currentLink && submenu) {
                this._setSubmenuState(currentLink, submenu, true);
            }
            current = current.parentElement?.closest("li");
        }
    },

    _isCurrentUrl(linkHref) {
        if (!linkHref) return false;
        try {
            const linkUrl = new URL(linkHref, window.location.origin);
            return linkUrl.pathname === window.location.pathname && linkUrl.search === window.location.search;
        } catch {
            return false;
        }
    },

    _decorateTopCategories() {
        document.querySelectorAll(".o_wsale_categories_grid a").forEach((card) => {
            if (card.dataset.wscaEnhanced === "true") return;
            card.dataset.wscaEnhanced = "true";
            card.classList.add("my_top_cat");
        });
    },

    _decorateProducts() {
        document.querySelectorAll(".oe_product").forEach((product) => {
            if (product.dataset.wscaEnhanced === "true") return;
            product.dataset.wscaEnhanced = "true";
            product.classList.add("my_product_card");
        });
    },

    _observeChanges() {
        let timeout;
        const observer = new MutationObserver(() => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this._decorateAll(), 100);
        });

        observer.observe(document.body, { childList: true, subtree: true });
        return observer;
    },
});
