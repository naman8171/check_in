/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

function parseFilterTokens(raw) {
    return (raw || "")
        .split(",")
        .map((token) => token.trim())
        .filter(Boolean);
}

function normalizeNumeric(value) {
    if (typeof value !== "string") {
        return Number.NaN;
    }
    return Number.parseFloat(value.replace(/,/g, "").trim());
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
        this._advancedFiltersByIndex = {};

        onMounted(() => {
            this._ensureAdvancedFilterRow();
            this._applyAdvancedFilters();
        });

        onPatched(() => {
            this._ensureAdvancedFilterRow();
            this._applyAdvancedFilters();
        });
    },

    _getListTableElement() {
        if (!this.el) {
            return null;
        }
        if (this.el.tagName === "TABLE") {
            return this.el;
        }
        return this.el.querySelector("table.o_list_table, table");
    },

    _ensureAdvancedFilterRow() {
        const table = this._getListTableElement();
        const thead = table?.querySelector("thead");
        if (!thead) {
            return;
        }

        const headerRow = thead.querySelector("tr");
        if (!headerRow) {
            return;
        }

        const previous = thead.querySelector("tr.o_advanced_filter_row");
        if (previous) {
            previous.remove();
        }

        const headerCells = [...headerRow.querySelectorAll("th")];
        if (!headerCells.length) {
            return;
        }

        const filterRow = document.createElement("tr");
        filterRow.className = "o_advanced_filter_row";

        headerCells.forEach((headerCell, index) => {
            const th = document.createElement("th");
            th.className = "o_advanced_filter_cell";

            const fieldName = headerCell.dataset?.name || "";
            const looksUtilityColumn = headerCell.classList.contains("o_list_record_selector")
                || headerCell.classList.contains("o_list_button")
                || headerCell.classList.contains("o_list_actions_header_cell");
            const hasVisibleTitle = Boolean(headerCell.textContent.trim());
            const isDataColumn = Boolean(fieldName) || (hasVisibleTitle && !looksUtilityColumn);

            if (!isDataColumn) {
                filterRow.appendChild(th);
                return;
            }

            const input = document.createElement("input");
            input.type = "text";
            input.className = "o_input o_advanced_filter_input";
            input.placeholder = headerCell.textContent.trim() || fieldName;
            input.value = this._advancedFiltersByIndex[index] || "";
            input.dataset.colIndex = String(index);

            input.addEventListener("input", (ev) => {
                this._advancedFiltersByIndex[index] = ev.target.value || "";
                this._applyAdvancedFilters();
            });

            input.addEventListener("keydown", (ev) => {
                if (ev.key === "Escape") {
                    ev.target.value = "";
                    this._advancedFiltersByIndex[index] = "";
                    this._applyAdvancedFilters();
                }
            });

            th.appendChild(input);
            filterRow.appendChild(th);
        });

        headerRow.insertAdjacentElement("afterend", filterRow);
    },

    _applyAdvancedFilters() {
        const table = this._getListTableElement();
        if (!table) {
            return;
        }

        const rows = table.querySelectorAll("tbody tr.o_data_row, tbody tr");
        if (!rows.length) {
            return;
        }

        const activeFilters = Object.entries(this._advancedFiltersByIndex)
            .map(([index, raw]) => ({ index: Number(index), tokens: parseFilterTokens(raw) }))
            .filter((entry) => entry.tokens.length);

        if (!activeFilters.length) {
            rows.forEach((row) => row.classList.remove("o_advanced_filter_hidden"));
            return;
        }

        rows.forEach((row) => {
            if (row.classList.contains("o_group_header")) {
                row.classList.remove("o_advanced_filter_hidden");
                return;
            }

            const cells = row.querySelectorAll("td");
            const rowMatches = activeFilters.every(({ index, tokens }) => {
                const cell = cells[index];
                if (!cell) {
                    return false;
                }
                const cellText = (cell.textContent || "").trim();
                const numericMode = tokens.every(tokenLooksNumeric);

                return tokens.some((token) => {
                    if (numericMode) {
                        return matchNumeric(cellText, token);
                    }
                    return matchText(cellText, token);
                });
            });

            row.classList.toggle("o_advanced_filter_hidden", !rowMatches);
        });
    },
});
