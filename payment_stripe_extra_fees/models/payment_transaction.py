# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    stripe_fee_amount = fields.Float(
        string='Stripe Fee Amount',
        digits=(16, 2),
        default=0.0,
        readonly=True,
        help='The extra Stripe fee amount computed and added to this transaction.',
    )
    stripe_fee_is_international = fields.Boolean(
        string='International Fee Applied',
        default=False,
        readonly=True,
        help='Indicates whether international fees were applied to this transaction.',
    )

    @api.model
    def _get_specific_create_values(self, provider_code, values):
        """Inject Stripe fees into transaction creation values before the provider request."""
        tx_values = super()._get_specific_create_values(provider_code, values)

        if provider_code != 'stripe':
            return tx_values

        provider = self.env['payment.provider'].sudo().browse(values.get('provider_id'))
        if not provider.exists() or not provider.stripe_add_extra_fees:
            return tx_values

        amount = values.get('amount')
        currency = self.env['res.currency'].browse(values.get('currency_id'))
        partner = self.env['res.partner'].browse(values.get('partner_id'))

        if not amount or not currency:
            return tx_values

        fee = provider._compute_stripe_fee(amount, currency, partner.country_id if partner else None)
        if fee <= 0:
            return tx_values

        is_international = provider._stripe_is_international(partner.country_id if partner else None)

        tx_values.update({
            'amount': amount + fee,
            'stripe_fee_amount': fee,
            'stripe_fee_is_international': is_international,
        })
        return tx_values

    @api.model_create_multi
    def create(self, vals_list):
        """Fallback coverage for flows that bypass _get_specific_create_values."""
        for vals in vals_list:
            provider = self.env['payment.provider'].sudo().browse(vals.get('provider_id'))
            if not provider.exists() or provider.code != 'stripe' or not provider.stripe_add_extra_fees:
                continue

            amount = vals.get('amount')
            currency = self.env['res.currency'].browse(vals.get('currency_id'))
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            if not amount or not currency:
                continue

            fee = provider._compute_stripe_fee(amount, currency, partner.country_id if partner else None)
            if fee <= 0:
                continue

            vals['stripe_fee_amount'] = fee
            vals['stripe_fee_is_international'] = provider._stripe_is_international(
                partner.country_id if partner else None
            )
            vals['amount'] = amount + fee

        transactions = super().create(vals_list)
        transactions._stripe_sync_fee_amount()
        return transactions

    def write(self, vals):
        res = super().write(vals)
        tracked = {'provider_id', 'provider_code', 'amount', 'currency_id', 'partner_id'}
        if not self.env.context.get('skip_stripe_fee_sync') and tracked.intersection(vals.keys()):
            self._stripe_sync_fee_amount()
        return res

    def _stripe_sync_fee_amount(self):
        for tx in self:
            if tx.provider_code != 'stripe' or not tx.provider_id.stripe_add_extra_fees:
                continue
            if not tx.currency_id or not tx.amount:
                continue

            base_amount = tx.amount - tx.stripe_fee_amount if tx.stripe_fee_amount else tx.amount
            fee = tx.provider_id._compute_stripe_fee(
                base_amount,
                tx.currency_id,
                tx.partner_id.country_id if tx.partner_id else None,
            )
            values = {
                'stripe_fee_amount': fee,
                'stripe_fee_is_international': tx.provider_id._stripe_is_international(
                    tx.partner_id.country_id if tx.partner_id else None
                ),
                'amount': base_amount + fee,
            }
            tx.with_context(skip_stripe_fee_sync=True).sudo().write(values)

    def _reconcile_after_done(self):
        res = super()._reconcile_after_done()

        for tx in self.filtered(
            lambda t: t.provider_code == 'stripe'
            and t.provider_id.stripe_add_extra_fees
            and t.stripe_fee_amount > 0
            and t.state == 'done'
        ):
            tx._create_stripe_fee_line()

        return res

    def _create_stripe_fee_line(self):
        self.ensure_one()

        provider = self.provider_id
        fee_product = provider.stripe_fee_product_id

        if not fee_product:
            _logger.warning('Stripe fee product missing for provider %s', provider.name)
            return

        fee_amount = self.stripe_fee_amount
        fee_label = _('Stripe Processing Fee (%s)') % (
            _('International') if self.stripe_fee_is_international else _('Domestic')
        )

        for sale_order in self.sale_order_ids:
            self._add_fee_to_sale_order(sale_order, fee_product, fee_amount, fee_label)

        for invoice in self.invoice_ids:
            self._add_fee_to_invoice(invoice, fee_product, fee_amount, fee_label)

    def _add_fee_to_sale_order(self, sale_order, fee_product, fee_amount, fee_label):
        if sale_order.state in ('cancel',):
            return

        existing = sale_order.order_line.filtered(
            lambda l: l.product_id == fee_product and 'Stripe' in l.name
        )
        if existing:
            return

        price_unit = fee_amount
        if self.currency_id != sale_order.currency_id:
            price_unit = self.currency_id._convert(
                fee_amount,
                sale_order.currency_id,
                sale_order.company_id,
                fields.Date.today(),
            )

        self.env['sale.order.line'].sudo().create({
            'order_id': sale_order.id,
            'product_id': fee_product.id,
            'name': fee_label,
            'product_uom_qty': 1.0,
            'price_unit': price_unit,
            'tax_id': [(6, 0, fee_product.taxes_id.ids)],
        })

    def _add_fee_to_invoice(self, invoice, fee_product, fee_amount, fee_label):
        if invoice.state == 'posted':
            return

        existing = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == fee_product
        )
        if existing:
            return

        price_unit = fee_amount
        if self.currency_id != invoice.currency_id:
            price_unit = self.currency_id._convert(
                fee_amount,
                invoice.currency_id,
                invoice.company_id,
                fields.Date.today(),
            )

        self.env['account.move.line'].sudo().create({
            'move_id': invoice.id,
            'product_id': fee_product.id,
            'name': fee_label,
            'quantity': 1.0,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, fee_product.taxes_id.ids)],
        })
