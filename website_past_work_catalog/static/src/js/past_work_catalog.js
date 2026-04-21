/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PastWorkCatalog = publicWidget.Widget.extend({
    selector: "#pastWorkCatalogRoot",

    events: {
        "change .past-work-filter": "_onFilterChange",
        "click #clearPastWorkFilters": "_onClearFilters",
        "click .past-work-expand": "_onExpand",
    },

    async start() {
        this.data = await this._rpc({ route: "/past-work/data" });
        this.items = this.data.items || [];
        this.activeSectors = new Set();
        this.activeWorkTypes = new Set();

        this._renderFilterGroup(
            this.el.querySelector("#sectorFilterContainer .filter-list"),
            this.data.filters?.sectors || [],
            "sector"
        );
        this._renderFilterGroup(
            this.el.querySelector("#workTypeFilterContainer .filter-list"),
            this.data.filters?.work_types || [],
            "work_type"
        );

        this._renderCards(this.items);
        return this._super(...arguments);
    },

    _renderFilterGroup(container, values, group) {
        container.innerHTML = "";
        for (const value of values) {
            const uid = `${group}-${value.replace(/\W+/g, "-").toLowerCase()}`;
            const html = `
                <label class="form-check mb-2" for="${uid}">
                    <input class="form-check-input past-work-filter" type="checkbox" id="${uid}" data-group="${group}" value="${_.escape(value)}">
                    <span class="form-check-label">${_.escape(value)}</span>
                </label>`;
            container.insertAdjacentHTML("beforeend", html);
        }
    },

    _matchesFilters(item) {
        const sectorMatch = !this.activeSectors.size || this.activeSectors.has(item.sector);
        const workTypeMatch = !this.activeWorkTypes.size || this.activeWorkTypes.has(item.work_type);
        return sectorMatch && workTypeMatch;
    },

    _renderCards(items) {
        const container = this.el.querySelector("#pastWorkCards");
        const count = this.el.querySelector("#pastWorkCount");
        const emptyState = this.el.querySelector("#pastWorkEmpty");

        container.innerHTML = "";
        count.textContent = `${items.length} project${items.length === 1 ? "" : "s"}`;
        emptyState.classList.toggle("d-none", !!items.length);

        for (const item of items) {
            const card = `
                <article class="past-work-card">
                    ${item.image_url ? `<div class="past-work-image"><img src="${_.escape(item.image_url)}" alt="${_.escape(item.name)}"></div>` : ""}
                    <div class="past-work-body">
                        <h3>${_.escape(item.name)}</h3>
                        <p class="past-work-short">${_.escape(item.short_description || "")}</p>
                        <button class="btn btn-link p-0 past-work-expand" type="button">View details</button>
                        <div class="past-work-details d-none mt-3">
                            <div class="small text-muted mb-2">${_.escape(item.sector)} · ${_.escape(item.work_type)}</div>
                            <p>${_.escape(item.description || "")}</p>
                            ${item.pdf_url ? `<a class="btn btn-primary btn-sm" href="${_.escape(item.pdf_url)}" target="_blank" rel="noopener">Download case study</a>` : ""}
                        </div>
                    </div>
                </article>`;
            container.insertAdjacentHTML("beforeend", card);
        }
    },

    _onFilterChange(ev) {
        const { group, value, checked } = ev.currentTarget.dataset.group
            ? { group: ev.currentTarget.dataset.group, value: ev.currentTarget.value, checked: ev.currentTarget.checked }
            : {};
        if (group === "sector") {
            checked ? this.activeSectors.add(value) : this.activeSectors.delete(value);
        }
        if (group === "work_type") {
            checked ? this.activeWorkTypes.add(value) : this.activeWorkTypes.delete(value);
        }
        this._renderCards(this.items.filter((item) => this._matchesFilters(item)));
    },

    _onClearFilters() {
        this.activeSectors.clear();
        this.activeWorkTypes.clear();
        this.el.querySelectorAll(".past-work-filter").forEach((el) => {
            el.checked = false;
        });
        this._renderCards(this.items);
    },

    _onExpand(ev) {
        const card = ev.currentTarget.closest(".past-work-body");
        const details = card.querySelector(".past-work-details");
        const isHidden = details.classList.contains("d-none");
        details.classList.toggle("d-none");
        ev.currentTarget.textContent = isHidden ? "Hide details" : "View details";
    },
});
