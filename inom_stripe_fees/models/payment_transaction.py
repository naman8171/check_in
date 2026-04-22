# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    extra_fees = fields.Monetary(
        string="Extra Fees",
        currency_field='currency_id',
        readonly=True,
        help="Surcharge added on top of the base amount for this transaction.",
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field='currency_id',
        readonly=True,
        help="Original amount before the surcharge was added.",
    )

    # -------------------------------------------------------------------------
    # Fee application: add fee to amount before Stripe sees it
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # Pre-compute fee from the incoming vals so the amount sent to Stripe
        # already includes the surcharge. We look up the provider + partner
        # country from the vals (they are provided by the generic payment flow).
        for vals in vals_list:
            self._inom_apply_fee(vals)
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # Helper with verbose logging so the admin can diagnose why a fee is or
    # isn't applied. Shows up in odoo.log as "odoo.addons.inom_stripe_fees...".
    # -------------------------------------------------------------------------
    def _inom_apply_fee(self, vals):
        provider_id = vals.get('provider_id')
        partner_id = vals.get('partner_id')
        amount = vals.get('amount') or 0.0

        if not provider_id:
            _logger.info("[inom_stripe_fees] skip: no provider_id in vals")
            return
        provider = self.env['payment.provider'].browse(provider_id)

        if provider.code != 'stripe':
            _logger.info(
                "[inom_stripe_fees] skip: provider is '%s' (not stripe)",
                provider.code,
            )
            return
        if not provider.fees_custom_active:
            _logger.info(
                "[inom_stripe_fees] skip: fees_custom_active is OFF on provider '%s'",
                provider.name,
            )
            return
        if not amount or amount <= 0:
            _logger.info("[inom_stripe_fees] skip: amount is %s", amount)
            return

        partner = self.env['res.partner'].browse(partner_id) if partner_id else None
        partner_country = partner.country_id if partner else False
        company_country = provider.company_id.country_id

        fee = provider._compute_custom_fees(amount, partner_country)
        _logger.info(
            "[inom_stripe_fees] provider=%s partner=%s partner_country=%s "
            "company_country=%s amount=%s -> fee=%s (dom=%s%%+%s, int=%s%%+%s, limit=%s)",
            provider.name,
            partner.display_name if partner else '<no-partner>',
            partner_country.code if partner_country else '<none>',
            company_country.code if company_country else '<none>',
            amount,
            fee,
            provider.fees_dom_var, provider.fees_dom_fixed,
            provider.fees_int_var, provider.fees_int_fixed,
            provider.fees_free_limit,
        )

        if fee:
            vals['base_amount'] = amount
            vals['extra_fees'] = fee
            vals['amount'] = amount + fee
            _logger.info(
                "[inom_stripe_fees] APPLIED fee=%s, new amount=%s",
                fee, vals['amount'],
            )
