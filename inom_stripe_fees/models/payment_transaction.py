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
            self._inom_sync_sale_order_fee_lines(vals, fee)
            vals['base_amount'] = amount
            vals['extra_fees'] = fee
            vals['amount'] = amount + fee
            _logger.info(
                "[inom_stripe_fees] APPLIED fee=%s, new amount=%s",
                fee, vals['amount'],
            )

    def _inom_sync_sale_order_fee_lines(self, vals, fee):
        """Keep website cart/order totals aligned with charged Stripe amount.

        If the transaction is linked to a sale order, create/update one
        technical fee line so order.amount_total matches tx.amount.
        """
        sale_order_ids = self._inom_extract_sale_order_ids(vals.get('sale_order_ids'))
        if not sale_order_ids:
            return

        orders = self.env['sale.order'].sudo().browse(sale_order_ids).exists()
        if not orders:
            return

        fee_product = self._inom_get_fee_product(orders.company_id[:1])
        if not fee_product:
            return

        for order in orders:
            existing_fee_lines = order.order_line.filtered('is_stripe_fee_line')
            if existing_fee_lines:
                existing_fee_lines.unlink()
            self.env['sale.order.line'].sudo().create({
                'order_id': order.id,
                'product_id': fee_product.id,
                'name': "Stripe Processing Fee",
                'product_uom_qty': 1.0,
                'price_unit': fee,
                'tax_ids': [(6, 0, [])],
                'is_stripe_fee_line': True,
            })

    def _inom_extract_sale_order_ids(self, sale_order_commands):
        """Extract m2m ids from standard command list."""
        order_ids = []
        if not sale_order_commands:
            return order_ids
        for command in sale_order_commands:
            if not isinstance(command, (list, tuple)) or len(command) < 1:
                continue
            if command[0] == 6 and len(command) >= 3:
                order_ids.extend(command[2] or [])
            elif command[0] == 4 and len(command) >= 2:
                order_ids.append(command[1])
        return list(set(order_ids))

    def _inom_get_fee_product(self, company):
        """Find or lazily create a product used for Stripe fee lines."""
        Product = self.env['product.product'].sudo()
        product = Product.search([('default_code', '=', 'INOM_STRIPE_FEE')], limit=1)
        if product:
            return product

        template_vals = {
            'name': "Stripe Processing Fee",
            'type': 'service',
            'sale_ok': False,
            'purchase_ok': False,
            'list_price': 0.0,
            'default_code': 'INOM_STRIPE_FEE',
            'company_id': company.id if company else False,
            'taxes_id': [(6, 0, [])],
        }
        template = self.env['product.template'].sudo().create(template_vals)
        return template.product_variant_id
