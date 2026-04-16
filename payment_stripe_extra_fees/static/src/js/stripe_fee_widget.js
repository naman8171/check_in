/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

const StripeFeeDisplay = {

    init() {
        console.log("✅ Stripe Fee JS Loaded");

        document.addEventListener('DOMContentLoaded', () => {
            this._bindEvents();
            this._refreshSelectedOption();
        });
    },

    _bindEvents() {
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="radio"]')) {

                const container = e.target.closest('.o_payment_option');
                if (!container) return;

                console.log("👉 Payment option changed");

                const providerCode = container.dataset.providerCode;
                const providerId = container.dataset.providerId || e.target.dataset.providerId;

                console.log("Provider Code:", providerCode);
                console.log("Provider ID:", providerId);

                if (providerCode === 'stripe') {
                    this._showFeeNotice(container, providerId);
                } else {
                    this._hideAllNotices();
                }
            }
        });

        document.addEventListener('click', () => {
            setTimeout(() => this._refreshSelectedOption(), 300);
        });
    },

    _refreshSelectedOption() {
        document.querySelectorAll('.o_payment_option').forEach((container) => {
            const selected = container.querySelector('input[type="radio"]:checked');
            if (!selected) return;

            const providerCode = container.dataset.providerCode;
            const providerId = container.dataset.providerId || selected.dataset.providerId;

            if (providerCode === 'stripe') {
                this._showFeeNotice(container, providerId);
            }
        });
    },

    async _showFeeNotice(container, providerId) {
        this._hideFeeNotice(container);

        if (!providerId) {
            console.log("❌ No provider ID");
            return;
        }

        try {
            const amount = this._getCurrentAmount();
            const currencyId = this._getCurrencyId();
            const partnerId = this._getPartnerId();

            console.log("🚀 Calling RPC...");
            console.log({ providerId, amount, currencyId, partnerId });

            const data = await rpc('/payment/stripe/fee_preview', {
                provider_id: providerId,
                amount: amount,
                currency_id: currencyId,
                partner_id: partnerId,
            });

            console.log("✅ RPC RESPONSE:", data);

            if (data && data.fee_amount > 0) {
                const feeEl = document.createElement('div');
                feeEl.className = 'o_stripe_fee_notice alert alert-warning mt-2';

                feeEl.innerHTML = `
                    <i class="fa fa-info-circle"></i>
                    ${_t('Stripe fee:')} <b>${data.fee_formatted}</b>
                `;

                container.appendChild(feeEl);
            } else {
                console.log("⚠ Fee = 0");
            }

        } catch (e) {
            console.error("❌ RPC ERROR:", e);
        }
    },

    _getCurrentAmount() {
        const el = document.querySelector('[data-amount]');
        if (el) return parseFloat(el.dataset.amount) || 0;

        const fallback = document.querySelector('.oe_currency_value');
        if (!fallback) return 0;

        return parseFloat(
            fallback.textContent.replace(/[^0-9.]/g, '')
        ) || 0;
    },

    _getCurrencyId() {
        const el = document.querySelector('[data-currency-id]');
        return el ? parseInt(el.dataset.currencyId) : false;
    },

    _getPartnerId() {
        const el = document.querySelector('[data-partner-id]');
        return el ? parseInt(el.dataset.partnerId) : false;
    },

    _hideFeeNotice(container) {
        const existing = container.querySelector('.o_stripe_fee_notice');
        if (existing) existing.remove();
    },

    _hideAllNotices() {
        document.querySelectorAll('.o_stripe_fee_notice').forEach(el => el.remove());
    },
};

StripeFeeDisplay.init();

export default StripeFeeDisplay;