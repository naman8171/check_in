/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSaleAnimatedUI = publicWidget.Widget.extend({
    selector: "body",

    start() {
        this._visibilityObserver = this._createVisibilityObserver();
        this._domObserver = this._observeChanges();

        this._decorateAll();
        return this._super(...arguments);
    },
    destroy() {
        if (this._domObserver) {
            this._domObserver.disconnect();
        }
        if (this._visibilityObserver) {
            this._visibilityObserver.disconnect();
        }
        this._super(...arguments);
    },

    _decorateAll() {
        this._decorateSidebar();
        this._decorateTopCategories();
        this._decorateProducts();
        this._syncCategoryHeaderFromActive();
    },

    _decorateSidebar() {
        const container = document.querySelector("#products_grid_before");
        if (!container) return;

        const links = container.querySelectorAll("a");
        links.forEach((link, index) => {
            if (link.dataset.wscaEnhanced !== "true") {
                link.dataset.wscaEnhanced = "true";
                link.classList.remove("nav-link");
                link.classList.add("my_sidebar_cat");
                link.style.animationDelay = `${Math.min(index * 60, 500)}ms`;
                this._observeVisibility(link);
            }

            if (link.dataset.wscaHeaderBound !== "true") {
                link.dataset.wscaHeaderBound = "true";
                link.addEventListener("click", () => {
                    this._setCategoryHeader(this._extractCategoryLabel(link));
                });
            }

            const submenu = this._getSubmenu(link);
            if (!submenu) {
                link.classList.remove("has-submenu");
                return;
            }

            link.classList.add("has-submenu");
            if (link.dataset.wscaToggleBound !== "true") {
                link.dataset.wscaToggleBound = "true";
                link.setAttribute("role", "button");
                link.setAttribute("aria-expanded", submenu.classList.contains("show") ? "true" : "false");
                link.addEventListener("click", (ev) => this._onSidebarClick(ev, container, link, submenu));
                link.addEventListener("keydown", (ev) => {
                    if (ev.key === "Enter" || ev.key === " ") {
                        this._onSidebarClick(ev, container, link, submenu);
                    }
                });
            }

            if (this._isCurrentUrl(link.href)) {
                link.classList.add("active");
                this._openAncestorMenus(link);
                this._setCategoryHeader(this._extractCategoryLabel(link));
            }
        });
    },

    _getSubmenu(link) {
        const listItem = link.closest("li");
        if (!listItem) return null;

        const directChild = Array.from(listItem.children).find((el) =>
            el.matches("ul, .collapse, .dropdown-menu, [data-wsca-submenu]")
        );
        if (directChild) return directChild;

        return listItem.querySelector("ul, .collapse, .dropdown-menu, [data-wsca-submenu]") || null;
    },

    _setSubmenuState(link, submenu, shouldOpen) {
        if (shouldOpen) {
            submenu.style.maxHeight = submenu.scrollHeight + "px";
            submenu.classList.add("open");
        } else {
            submenu.style.maxHeight = "0px";
            submenu.classList.remove("open");
        }

        link.classList.toggle("active", shouldOpen);
        link.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
    },

    _onSidebarClick(event, container, link, submenu) {
        event.preventDefault();
        event.stopPropagation();

        const isOpen = submenu.classList.contains("open") || submenu.classList.contains("show");

        container.querySelectorAll("ul.open, ul.show").forEach((el) => {
            if (el !== submenu) {
                el.classList.remove("open", "show");
            }
        });

        container.querySelectorAll("a.active").forEach((el) => {
            if (el !== link && this._getSubmenu(el)) {
                el.classList.remove("active");
                el.setAttribute("aria-expanded", "false");
            }
        });

        this._setSubmenuState(link, submenu, !isOpen);
        this._setCategoryHeader(this._extractCategoryLabel(link));
    },

    _openAncestorMenus(link) {
        let current = link.closest("li");
        while (current) {
            const currentLink = current.querySelector(":scope > a") || current.querySelector("a");
            const submenu = Array.from(current.children).find((el) => el.tagName === "UL") || current.querySelector("ul");

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
            return linkUrl.pathname === window.location.pathname;
        } catch {
            return false;
        }
    },

    _decorateTopCategories() {
        document.querySelectorAll(".o_wsale_categories_grid a").forEach((card, index) => {
            if (card.dataset.wscaEnhanced === "true") return;

            card.dataset.wscaEnhanced = "true";
            card.classList.add("my_top_cat");
            card.style.animationDelay = `${Math.min(index * 90, 700)}ms`;
            this._observeVisibility(card);
        });
    },

    _decorateProducts() {
        document.querySelectorAll(".oe_product").forEach((product, index) => {
            if (product.dataset.wscaEnhanced === "true") return;

            product.dataset.wscaEnhanced = "true";
            product.classList.add("my_product_card");
            product.style.animationDelay = `${Math.min(index * 45, 500)}ms`;
            this._observeVisibility(product);
        });
    },


    _extractCategoryLabel(link) {
        if (!link) return "";
        const clone = link.cloneNode(true);
        clone.querySelectorAll(".badge, .fa, .o_wsale_product_count").forEach((el) => el.remove());
        return (clone.textContent || "").replace(/\s+/g, " ").trim();
    },

    _setCategoryHeader(label) {
        const cleanLabel = (label || "").trim();
        if (!cleanLabel) return;

        const targets = document.querySelectorAll(
            ".o_wsale_products_main_row h1, .o_wsale_products_main_row .h1, .o_wsale_products_main_row h2, .o_wsale_products_main_row .h2"
        );
        targets.forEach((el) => {
            el.textContent = cleanLabel.toUpperCase();
            el.classList.add("wsca_category_header");
        });
    },

    _syncCategoryHeaderFromActive() {
        const activeLink = document.querySelector(
            "#products_grid_before a.active, #products_grid_before a[aria-expanded='true'], #products_grid_before a.text-danger"
        );
        if (!activeLink) return;
        this._setCategoryHeader(this._extractCategoryLabel(activeLink));
    },

    _createVisibilityObserver() {
        if (!("IntersectionObserver" in window)) return null;

        return new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.dataset.wscaVisible = "true";
                    }
                });
            },
            {
                threshold: 0.18,
                rootMargin: "0px 0px -8% 0px",
            }
        );
    },

    _observeVisibility(element) {
        if (this._visibilityObserver) {
            this._visibilityObserver.observe(element);
        } else {
            element.dataset.wscaVisible = "true";
        }
    },

    _observeChanges() {
        let timeout;
        const observer = new MutationObserver(() => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this._decorateAll(), 120);
        });

        observer.observe(document.body, { childList: true, subtree: true });
        return observer;
    },
});
