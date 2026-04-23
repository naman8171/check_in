/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useState, useEffect } from "@odoo/owl";

function toNumber(value) {
    if (typeof value !== "string") {
        return Number.NaN;
    }
    const normalized = value.replace(/,/g, "").trim();
    return Number.parseFloat(normalized);
}

function splitFilters(rawValue) {
    return (rawValue || "")
        .split(",")
        .map((part) => part.trim())
        .filter(Boolean);
}

function evaluateNumeric(cellText, token) {
    const match = token.match(/^(>=|<=|>|<|=)?\s*(-?\d+(?:\.\d+)?)$/);
    if (!match) {
        return false;
    }
    const operator = match[1] || "=";
    const value = Number.parseFloat(match[2]);
    const cellValue = toNumber(cellText);
    if (Number.isNaN(cellValue)) {
        return false;
    }

    if (operator === ">") {
        return cellValue > value;
    }
    if (operator === "<") {
        return cellValue < value;
    }
    if (operator === ">=") {
        return cellValue >= value;
    }
    if (operator === "<=") {
        return cellValue <= value;
    }
    return cellValue === value;
}

function evaluateText(cellText, token) {
    return cellText.toLowerCase().includes(token.toLowerCase());
}

patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.advancedFilterState = useState({
            filters: {},
        });

        useEffect(
            () => {
                this.applyAdvancedFilters();
            },
            () => [JSON.stringify(this.advancedFilterState.filters), this.props.list?.records?.length || 0]
        );
    },

    get advancedFilterColumns() {
        return this.columns.filter((column) => {
            const name = column?.name;
            if (!name) {
                return false;
            }
            if (column.type === "button_group") {
                return false;
            }
            return true;
        });
    },

    onAdvancedFilterInput(columnName, ev) {
        this.advancedFilterState.filters[columnName] = ev.target.value || "";
    },

    onAdvancedFilterKeydown(ev) {
        if (ev.key === "Escape") {
            ev.target.value = "";
            const columnName = ev.target.dataset.columnName;
            this.advancedFilterState.filters[columnName] = "";
        }
    },

    clearAdvancedFilters() {
        Object.keys(this.advancedFilterState.filters).forEach((key) => {
            this.advancedFilterState.filters[key] = "";
        });
    },

    getAdvancedFilterValue(columnName) {
        return this.advancedFilterState.filters[columnName] || "";
    },

    applyAdvancedFilters() {
        if (!this.el) {
            return;
        }

        const tableRows = this.el.querySelectorAll("tbody tr.o_data_row");
        if (!tableRows.length) {
            return;
        }

        const activeFilters = Object.entries(this.advancedFilterState.filters)
            .map(([fieldName, value]) => [fieldName, splitFilters(value)])
            .filter(([, tokens]) => tokens.length);

        if (!activeFilters.length) {
            tableRows.forEach((row) => {
                row.classList.remove("o_advanced_filter_hidden");
            });
            return;
        }

        const columnIndexByName = new Map();
        this.columns.forEach((column, index) => {
            if (column?.name) {
                columnIndexByName.set(column.name, index);
            }
        });

        tableRows.forEach((row) => {
            const cells = row.querySelectorAll("td");
            const matchesAllColumns = activeFilters.every(([fieldName, tokens]) => {
                const colIdx = columnIndexByName.get(fieldName);
                if (colIdx === undefined) {
                    return true;
                }
                const cell = cells[colIdx];
                if (!cell) {
                    return false;
                }
                const cellText = (cell.textContent || "").trim();
                const numericHint = tokens.every((token) => /^(>=|<=|>|<|=)?\s*-?\d+(?:\.\d+)?$/.test(token));

                return tokens.some((token) => {
                    if (numericHint) {
                        return evaluateNumeric(cellText, token);
                    }
                    return evaluateText(cellText, token);
                });
            });

            row.classList.toggle("o_advanced_filter_hidden", !matchesAllColumns);
        });
    },
});
