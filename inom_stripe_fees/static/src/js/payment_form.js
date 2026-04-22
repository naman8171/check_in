/** @odoo-module **/
/**
 * Inom Stripe Transaction Fees — payment-form display
 * ----------------------------------------------------
 * Reads fee config from /inom_stripe_fees/config and injects a
 * Base / Fee / Total breakdown into the payment modal whenever the
 * Stripe option is selected.
 *
 * (c) InomERP Pvt Ltd — https://inomerp.in — info@inomerp.in
 */
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

const BREAKDOWN_CLASS = "inom-fee-breakdown";
const SUMMARY_FEE_CLASS = "inom-summary-fee-row";
const SUMMARY_TOTAL_ATTR = "data-inom-summary-total-original";

publicWidget.registry.InomStripeFeeDisplay = publicWidget.Widget.extend({
    // Match every flow that renders a payment form: website checkout,
    // invoice portal, /my/payment, donation page, etc.
    selector:
        "form[name='o_payment_form'], " +
        "#o_payment_form, " +
        ".o_payment_form, " +
        "#wrapwrap:has(input[name='o_payment_radio'])",

    events: {
        "change input[name='o_payment_radio']": "_onProviderChange",
    },

    async start() {
        await this._super(...arguments);
        try {
            this.feeConfig = await rpc(
                "/inom_stripe_fees/config",
                this._extractPortalContext()
            );
        } catch (e) {
            // Silent fail — user will simply not see the breakdown.
            this.feeConfig = null;
        }
        if (!this.feeConfig?.active) return;
        // Render once on load in case Stripe is pre-selected.
        this._renderBreakdown();
    },

    /**
     * Extract order_id / invoice_id / access_token from the current URL so
     * the backend can resolve the correct partner (critical for portal
     * "pay by email link" flows where the user may not be logged in).
     */
    _extractPortalContext() {
        const ctx = {};
        try {
            const params = new URLSearchParams(window.location.search);
            if (params.has("access_token")) {
                ctx.access_token = params.get("access_token");
            }
            const path = window.location.pathname;
            const orderMatch = path.match(/\/my\/(orders|quotes)\/(\d+)/);
            if (orderMatch) ctx.order_id = parseInt(orderMatch[2], 10);
            const invoiceMatch = path.match(/\/my\/invoices\/(\d+)/);
            if (invoiceMatch) ctx.invoice_id = parseInt(invoiceMatch[1], 10);
        } catch (e) {
            // Ignore — fall back to empty context.
        }
        return ctx;
    },

    _onProviderChange() {
        this._renderBreakdown();
    },

    _renderBreakdown() {
        this._removeBreakdown();
        if (!this.feeConfig?.active) return;

        const stripeRadio = this._findStripeRadio();
        if (!stripeRadio || !stripeRadio.checked) return;

        const baseAmount = this._getBaseAmount();
        if (!baseAmount || baseAmount <= 0) return;

        const { pct, fixed, free_limit } = this.feeConfig;
        if (free_limit && baseAmount > free_limit) return;

        const fee = (baseAmount * (pct || 0)) / 100 + (fixed || 0);
        if (fee <= 0) return;

        this._injectBreakdown(baseAmount, fee, baseAmount + fee);
        this._injectSummaryFee(fee);
    },

    // -----------------------------------------------------------------
    // Helpers
    // -----------------------------------------------------------------
    _findStripeRadio() {
        // Look globally — the payment form may be in a modal outside `this.el`.
        const root = document;
        return (
            root.querySelector(
                "input[name='o_payment_radio'][data-provider-code='stripe']:checked"
            ) ||
            root.querySelector(
                "input[name='o_payment_radio'][data-provider-code='stripe']"
            )
        );
    },

    _getBaseAmount() {
        // Try several places Odoo commonly exposes the amount.
        const selectors = [
            "[name='amount']",
            "input[name='amount']",
            "[data-amount]",
            ".o_portal_my_doc_table .o_portal_my_doc_amount",
            "#o_payment_summary_amount",
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (!el) continue;
            const raw =
                el.value ||
                el.dataset.amount ||
                el.getAttribute("data-amount") ||
                el.textContent ||
                "";
            const num = parseFloat(String(raw).replace(/[^\d.-]/g, ""));
            if (!isNaN(num) && num > 0) return num;
        }

        // Last-resort: scan the modal header/body for a currency-looking
        // value near an "Amount" label.
        const amountLabel = [...document.querySelectorAll("*")].find(
            (n) =>
                n.children.length === 0 &&
                /^\s*Amount\s*$/i.test(n.textContent || "")
        );
        if (amountLabel) {
            const sibling =
                amountLabel.nextElementSibling ||
                amountLabel.parentElement?.nextElementSibling;
            if (sibling) {
                const num = parseFloat(
                    String(sibling.textContent).replace(/[^\d.-]/g, "")
                );
                if (!isNaN(num) && num > 0) return num;
            }
        }
        return 0;
    },

    _formatCurrency(amount) {
        const sym = this.feeConfig.currency_symbol || "";
        const pos = this.feeConfig.currency_position || "before";
        const val = amount.toFixed(2);
        return pos === "after" ? `${val} ${sym}` : `${sym} ${val}`;
    },

    _injectBreakdown(base, fee, total) {
        const stripeRadio = this._findStripeRadio();
        if (!stripeRadio) return;

        // Try to attach to the Stripe payment option container; fall back
        // to the payment form itself.
        const anchor =
            stripeRadio.closest(
                ".o_payment_option_card, .form-check, label, li"
            ) ||
            document.querySelector("form[name='o_payment_form'], #o_payment_form, .o_payment_form");
        if (!anchor) return;

        const div = document.createElement("div");
        div.className = `${BREAKDOWN_CLASS} alert alert-info mt-2 mb-0 py-2 px-3 small`;
        div.innerHTML = `
            <div class="d-flex justify-content-between">
                <span>Base amount</span>
                <strong>${this._formatCurrency(base)}</strong>
            </div>
            <div class="d-flex justify-content-between">
                <span>Stripe processing fee</span>
                <strong>+ ${this._formatCurrency(fee)}</strong>
            </div>
            <hr class="my-1"/>
            <div class="d-flex justify-content-between">
                <span><strong>Total to be charged</strong></span>
                <strong>${this._formatCurrency(total)}</strong>
            </div>
        `;
        anchor.insertAdjacentElement("afterend", div);
    },

    _removeBreakdown() {
        document
            .querySelectorAll(`.${BREAKDOWN_CLASS}`)
            .forEach((n) => n.remove());
        document
            .querySelectorAll(`.${SUMMARY_FEE_CLASS}`)
            .forEach((n) => n.remove());
        this._restoreSummaryTotal();
    },

    _injectSummaryFee(fee) {
        const totalLabel = [...document.querySelectorAll("div,span,strong,p")].find(
            (el) => el.children.length === 0 && /^\s*Total\s*$/i.test(el.textContent || "")
        );
        if (!totalLabel) return;
        const totalAmountEl = totalLabel.parentElement?.querySelector("strong, span:last-child");
        if (!totalAmountEl) return;

        if (!totalAmountEl.getAttribute(SUMMARY_TOTAL_ATTR)) {
            totalAmountEl.setAttribute(SUMMARY_TOTAL_ATTR, totalAmountEl.textContent || "");
        }

        const currentTotal = parseFloat(
            String(totalAmountEl.getAttribute(SUMMARY_TOTAL_ATTR)).replace(/[^\d.-]/g, "")
        );
        if (isNaN(currentTotal) || currentTotal <= 0) return;

        const feeRow = document.createElement("div");
        feeRow.className = `${SUMMARY_FEE_CLASS} d-flex justify-content-between`;
        feeRow.innerHTML = `
            <span>Stripe processing fee</span>
            <span>${this._formatCurrency(fee)}</span>
        `;
        totalLabel.parentElement.insertAdjacentElement("beforebegin", feeRow);
        totalAmountEl.textContent = this._formatCurrency(currentTotal + fee);
    },

    _restoreSummaryTotal() {
        document.querySelectorAll(`[${SUMMARY_TOTAL_ATTR}]`).forEach((el) => {
            el.textContent = el.getAttribute(SUMMARY_TOTAL_ATTR);
            el.removeAttribute(SUMMARY_TOTAL_ATTR);
        });
    },
});
