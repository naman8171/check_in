/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

const StripeFeeDisplay = {

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this._bindEvents();
        });
    },

    /**
     * Bind change event on payment methods
     */
    _bindEvents() {
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="radio"]') && (
                e.target.name === 'o_payment_radio' ||
                e.target.name === 'payment_option_id' ||
                e.target.name === 'provider_id'
            )) {
                const container = e.target.closest('.o_payment_option');

                if (!container) return;

                // Check if Stripe selected
                if (container.dataset.providerCode === 'stripe') {
                    const providerId = container.dataset.providerId || e.target.dataset.providerId;
                    this._showFeeNotice(container, providerId);
                } else {
                    this._hideAllNotices();
                }
            }
        });
    },

    /**
     * Show fee notice
     */
    async _showFeeNotice(container, providerId) {
        this._hideFeeNotice(container);

        if (!providerId) return;

        try {
            const amount = this._getCurrentAmount();
            const currencyId = this._getCurrencyId(container);
            const partnerId = this._getPartnerId(container);

            const data = await rpc('/payment/stripe/fee_preview', {
                provider_id: providerId,
                amount: amount,
                currency_id: currencyId,
                partner_id: partnerId,
            });

            if (data && data.fee_amount > 0) {
                const feeEl = document.createElement('div');
                feeEl.className = 'o_stripe_fee_notice alert alert-info mt-2 py-1 px-2';
                feeEl.style.fontSize = '0.85rem';

                feeEl.innerHTML = `
                    <i class="fa fa-info-circle me-1"></i>
                    ${_t('A processing fee of')} <strong>${data.fee_formatted}</strong>
                    ${_t('will be added to your order total.')}
                `;

                container.appendChild(feeEl);
            }

        } catch (e) {
            // silent by design
        }
    },

    _getCurrentAmount() {
        const amountNode = document.querySelector('[data-amount]');
        if (amountNode && amountNode.dataset.amount) {
            return parseFloat(amountNode.dataset.amount) || 0;
        }

        const textNode = document.querySelector('.o_payment_summary [data-oe-expression="amount"]')
            || document.querySelector('.modal .o_amount')
            || document.querySelector('.oe_currency_value');
        if (!textNode) return 0;

        const value = (textNode.textContent || '').replace(/[^0-9.,-]/g, '').replace(',', '');
        return parseFloat(value) || 0;
    },

    _getCurrencyId(container) {
        const form = container.closest('form');
        const currencyInput = form && form.querySelector('input[name="currency_id"]');
        if (currencyInput && currencyInput.value) {
            return parseInt(currencyInput.value, 10);
        }

        const amountNode = document.querySelector('[data-currency-id]');
        return amountNode ? parseInt(amountNode.dataset.currencyId, 10) : false;
    },

    _getPartnerId(container) {
        const form = container.closest('form');
        const partnerInput = form && form.querySelector('input[name="partner_id"]');
        if (partnerInput && partnerInput.value) {
            return parseInt(partnerInput.value, 10);
        }

        const partnerNode = document.querySelector('[data-partner-id]');
        return partnerNode ? parseInt(partnerNode.dataset.partnerId, 10) : false;
    },

    /**
     * Remove notice from specific container
     */
    _hideFeeNotice(container) {
        const existing = container.querySelector('.o_stripe_fee_notice');
        if (existing) existing.remove();
    },

    /**
     * Remove all notices
     */
    _hideAllNotices() {
        document.querySelectorAll('.o_stripe_fee_notice').forEach(el => el.remove());
    },
};

StripeFeeDisplay.init();

export default StripeFeeDisplay;
