/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

function normalizeNumeric(value) {
    if (typeof value !== "string") {
        return Number.NaN;
    }
    return Number.parseFloat(value.replace(/,/g, "").trim());
}

function parseFilterTokens(raw) {
    return (raw || "")
        .split(",")
        .map((token) => token.trim())
        .filter(Boolean);
}

function tokenLooksNumeric(token) {
    return /^(>=|<=|>|<|=)?\s*-?\d+(?:\.\d+)?$/.test(token);
}

function matchNumeric(cellText, token) {
    const match = token.match(/^(>=|<=|>|<|=)?\s*(-?\d+(?:\.\d+)?)$/);
    if (!match) {
        return false;
    }

    const operator = match[1] || "=";
    const expected = Number.parseFloat(match[2]);
    const actual = normalizeNumeric(cellText);
    if (Number.isNaN(actual)) {
        return false;
    }

    if (operator === ">") return actual > expected;
    if (operator === "<") return actual < expected;
    if (operator === ">=") return actual >= expected;
    if (operator === "<=") return actual <= expected;
    return actual === expected;
}

function matchText(cellText, token) {
    return cellText.toLowerCase().includes(token.toLowerCase());
}

patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this._advancedFilters = {};

        onMounted(() => {
            this._renderAdvancedFilterRow();
            this._applyAdvancedFilters();
        });

        onPatched(() => {
            this._renderAdvancedFilterRow();
            this._applyAdvancedFilters();
        });
    },

    _renderAdvancedFilterRow() {
        if (!this.el) {
            return;
        }

        const thead = this.el.querySelector("table thead");
        if (!thead) {
            return;
        }

        const headerRow = thead.querySelector("tr");
        if (!headerRow) {
            return;
        }

        const oldRow = thead.querySelector("tr.o_advanced_filter_row");
        if (oldRow) {
            oldRow.remove();
        }

        const filterRow = document.createElement("tr");
        filterRow.className = "o_advanced_filter_row";

        this.columns.forEach((column, index) => {
            const th = document.createElement("th");
            th.className = "o_advanced_filter_cell";

            if (!column?.name) {
                filterRow.appendChild(th);
                return;
            }

            const input = document.createElement("input");
            input.type = "text";
            input.className = "o_input o_advanced_filter_input";
            input.placeholder = column.string || column.name;
            input.value = this._advancedFilters[column.name] || "";
            input.dataset.columnName = column.name;
            input.dataset.columnIndex = String(index);

            input.addEventListener("input", (ev) => {
                this._advancedFilters[column.name] = ev.target.value || "";
                this._applyAdvancedFilters();
            });

            input.addEventListener("keydown", (ev) => {
                if (ev.key === "Escape") {
                    ev.target.value = "";
                    this._advancedFilters[column.name] = "";
                    this._applyAdvancedFilters();
                }
            });

            th.appendChild(input);
            filterRow.appendChild(th);
        });

        headerRow.insertAdjacentElement("afterend", filterRow);
    },

    _applyAdvancedFilters() {
        if (!this.el) {
            return;
        }

        const rows = this.el.querySelectorAll("tbody tr.o_data_row");
        if (!rows.length) {
            return;
        }

        const activeFilters = Object.entries(this._advancedFilters)
            .map(([field, raw]) => ({ field, tokens: parseFilterTokens(raw) }))
            .filter((entry) => entry.tokens.length > 0);

        if (!activeFilters.length) {
            rows.forEach((row) => row.classList.remove("o_advanced_filter_hidden"));
            return;
        }

        const indexByField = new Map();
        this.columns.forEach((column, index) => {
            if (column?.name) {
                indexByField.set(column.name, index);
            }
        });

        rows.forEach((row) => {
            const cells = row.querySelectorAll("td");

            const rowMatches = activeFilters.every(({ field, tokens }) => {
                const idx = indexByField.get(field);
                if (idx === undefined) {
                    return true;
                }
                const cell = cells[idx];
                if (!cell) {
                    return false;
                }

                const cellText = (cell.textContent || "").trim();
                const useNumeric = tokens.every(tokenLooksNumeric);

                return tokens.some((token) => {
                    if (useNumeric) {
                        return matchNumeric(cellText, token);
                    }
                    return matchText(cellText, token);
                });
            });

            row.classList.toggle("o_advanced_filter_hidden", !rowMatches);
        });
    },
});
