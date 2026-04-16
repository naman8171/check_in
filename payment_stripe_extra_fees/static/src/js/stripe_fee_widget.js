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
            if (e.target.name === 'o_payment_radio') {
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
            console.log("Stripe provider ID:", providerId);

            const data = await rpc('/payment/stripe/fee_preview', {
                provider_id: providerId,
            });

            console.log("Stripe fee response:", data);

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
            console.log('Stripe fee error:', e);
        }
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
