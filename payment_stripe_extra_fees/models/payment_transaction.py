# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # -------------------------------------------------------------------------
    # Fee Tracking Fields on Transaction
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Helper: Compute Fee
    # -------------------------------------------------------------------------
    @api.model
    def _stripe_compute_and_apply_fee(self, provider, amount, currency, partner):
        print("\n===== STRIPE TX DEBUG: COMPUTE FEE START =====")
        print("Provider:", provider.name if provider else None)
        print("Amount:", amount)
        print("Currency:", currency.name if currency else None)
        print("Partner:", partner.name if partner else None)

        partner_country = partner.country_id if partner else None
        print("Partner Country:", partner_country.name if partner_country else None)

        fee = provider._compute_stripe_fee(amount, currency, partner_country)

        print("Computed Fee from provider:", fee)
        print("===== STRIPE TX DEBUG: COMPUTE FEE END =====\n")

        return fee

    # -------------------------------------------------------------------------
    # CREATE OVERRIDE
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        print("\n========== STRIPE TRANSACTION CREATE DEBUG ==========")

        transactions = super().create(vals_list)

        for tx in transactions:
            print("\n--- TX DEBUG START ---")
            print("TX Reference:", tx.reference)
            print("Provider:", tx.provider_id.code if tx.provider_id else None)
            print("Amount:", tx.amount)
            print("Currency:", tx.currency_id.name if tx.currency_id else None)
            print("Partner:", tx.partner_id.name if tx.partner_id else None)

            # ================= SAFE DEBUG CHECKS =================
            provider = tx.provider_id

            if not provider:
                print("❌ No provider found -> SKIPPING")
                print("--- TX DEBUG END ---\n")
                continue

            print("DEBUG Provider ID:", provider.id)
            print("DEBUG Provider Name:", provider.name)
            print("DEBUG Provider Code:", provider.code)
            print("DEBUG Extra Fees Enabled:", provider.stripe_add_extra_fees)

            # ================= FIXED CONDITION =================
            is_stripe = provider.code == 'stripe'
            has_fees_enabled = bool(provider.stripe_add_extra_fees)
            valid_amount = tx.amount and tx.amount > 0

            print("DEBUG is_stripe:", is_stripe)
            print("DEBUG has_fees_enabled:", has_fees_enabled)
            print("DEBUG valid_amount:", valid_amount)

            if is_stripe and has_fees_enabled and valid_amount:
                print("✅ Stripe fee condition PASSED")

                try:
                    partner = tx.partner_id

                    fee = self._stripe_compute_and_apply_fee(
                        provider,
                        tx.amount,
                        tx.currency_id,
                        partner,
                    )

                    print("Fee returned:", fee)

                    if fee > 0:
                        is_international = provider._stripe_is_international(
                            partner.country_id if partner else None
                        )

                        print("Is International:", is_international)
                        print("Writing fee into transaction...")

                        tx.sudo().write({
                            'stripe_fee_amount': fee,
                            'stripe_fee_is_international': is_international,
                            'amount': tx.amount + fee,
                        })

                        print("UPDATED TX AMOUNT:", tx.amount + fee)

                    else:
                        print("⚠ Fee is 0")

                except Exception as e:
                    print("❌ ERROR in fee computation:", str(e))

            else:
                print("❌ Stripe fee condition FAILED")
                print("Reason breakdown:")
                print("  - is_stripe:", is_stripe)
                print("  - has_fees_enabled:", has_fees_enabled)
                print("  - valid_amount:", valid_amount)

            print("--- TX DEBUG END ---\n")

        print("========== STRIPE TRANSACTION CREATE END ==========\n")

        return transactions

    # -------------------------------------------------------------------------
    # AFTER DONE RECONCILE
    # -------------------------------------------------------------------------
    def _reconcile_after_done(self):
        print("\n========== STRIPE RECONCILE DEBUG ==========")

        res = super()._reconcile_after_done()

        for tx in self.filtered(
            lambda t: t.provider_id.code == 'stripe'
            and t.provider_id.stripe_add_extra_fees
            and t.stripe_fee_amount > 0
            and t.state == 'done'
        ):
            print("Processing DONE TX:", tx.reference)
            tx._create_stripe_fee_line()

        print("========== STRIPE RECONCILE END ==========\n")

        return res

    # -------------------------------------------------------------------------
    # CREATE FEE LINE
    # -------------------------------------------------------------------------
    def _create_stripe_fee_line(self):
        self.ensure_one()

        print("\n===== STRIPE FEE LINE DEBUG =====")
        print("TX:", self.reference)

        provider = self.provider_id
        fee_product = provider.stripe_fee_product_id

        print("Fee Product:", fee_product.name if fee_product else None)

        if not fee_product:
            print("STOP: No fee product configured")
            _logger.warning(
                'Stripe fee product missing for provider %s',
                provider.name
            )
            return

        fee_amount = self.stripe_fee_amount
        fee_label = _('Stripe Processing Fee (%s)') % (
            _('International') if self.stripe_fee_is_international else _('Domestic')
        )

        print("Fee Amount:", fee_amount)
        print("Fee Label:", fee_label)

        for sale_order in self.sale_order_ids:
            print("Adding fee to Sale Order:", sale_order.name)
            self._add_fee_to_sale_order(sale_order, fee_product, fee_amount, fee_label)

        for invoice in self.invoice_ids:
            print("Adding fee to Invoice:", invoice.name)
            self._add_fee_to_invoice(invoice, fee_product, fee_amount, fee_label)

        print("===== STRIPE FEE LINE DEBUG END =====\n")

    # -------------------------------------------------------------------------
    # SALE ORDER FEE
    # -------------------------------------------------------------------------
    def _add_fee_to_sale_order(self, sale_order, fee_product, fee_amount, fee_label):
        print("DEBUG: Sale Order Fee Add ->", sale_order.name)

        if sale_order.state in ('cancel',):
            print("Skipped cancelled SO")
            return

        existing = sale_order.order_line.filtered(
            lambda l: l.product_id == fee_product and 'Stripe' in l.name
        )

        if existing:
            print("Fee already exists in SO")
            return

        price_unit = fee_amount

        if self.currency_id != sale_order.currency_id:
            print("Currency conversion for SO")
            price_unit = self.currency_id._convert(
                fee_amount,
                sale_order.currency_id,
                sale_order.company_id,
                fields.Date.today(),
            )

        print("Final SO fee price:", price_unit)

        self.env['sale.order.line'].sudo().create({
            'order_id': sale_order.id,
            'product_id': fee_product.id,
            'name': fee_label,
            'product_uom_qty': 1.0,
            'price_unit': price_unit,
            'tax_id': [(6, 0, fee_product.taxes_id.ids)],
        })

    # -------------------------------------------------------------------------
    # INVOICE FEE
    # -------------------------------------------------------------------------
    def _add_fee_to_invoice(self, invoice, fee_product, fee_amount, fee_label):
        print("DEBUG: Invoice Fee Add ->", invoice.name)

        if invoice.state == 'posted':
            print("Skipped posted invoice")
            return

        existing = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == fee_product
        )

        if existing:
            print("Fee already exists in invoice")
            return

        price_unit = fee_amount

        if self.currency_id != invoice.currency_id:
            print("Currency conversion for invoice")
            price_unit = self.currency_id._convert(
                fee_amount,
                invoice.currency_id,
                invoice.company_id,
                fields.Date.today(),
            )

        print("Final invoice fee price:", price_unit)

        self.env['account.move.line'].sudo().create({
            'move_id': invoice.id,
            'product_id': fee_product.id,
            'name': fee_label,
            'quantity': 1.0,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, fee_product.taxes_id.ids)],
        })

    # -------------------------------------------------------------------------
    # BREAKDOWN
    # -------------------------------------------------------------------------
    def get_stripe_fee_breakdown(self):
        self.ensure_one()

        print("DEBUG: get_stripe_fee_breakdown called")

        data = {
            'fee_amount': self.stripe_fee_amount,
            'fee_type': _('International') if self.stripe_fee_is_international else _('Domestic'),
            'original_amount': self.amount - self.stripe_fee_amount,
            'total_amount': self.amount,
        }

        print("Breakdown:", data)
        return data