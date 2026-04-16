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
    )

    stripe_fee_is_international = fields.Boolean(
        string='International Fee Applied',
        default=False,
        readonly=True,
    )

    # =====================================================
    # STEP 1: BEFORE TRANSACTION CREATE (MOST IMPORTANT)
    # =====================================================
    @api.model
    def _get_specific_create_values(self, provider_code, values):
        print("\n🔥 STEP 1: _get_specific_create_values CALLED")
        print("Provider Code:", provider_code)
        print("Incoming Values:", values)

        tx_values = super()._get_specific_create_values(provider_code, values)

        if provider_code != 'stripe':
            print("❌ Not Stripe -> SKIP")
            return tx_values

        provider = self.env['payment.provider'].sudo().browse(values.get('provider_id'))

        print("Provider:", provider.name)
        print("Extra Fees Enabled:", provider.stripe_add_extra_fees)

        if not provider.exists() or not provider.stripe_add_extra_fees:
            print("❌ Provider invalid or fees disabled")
            return tx_values

        amount = values.get('amount')
        currency = self.env['res.currency'].browse(values.get('currency_id'))
        partner = self.env['res.partner'].browse(values.get('partner_id'))

        print("Amount:", amount)
        print("Currency:", currency.name if currency else None)
        print("Partner:", partner.name if partner else None)

        if not amount or not currency:
            print("❌ Missing amount/currency")
            return tx_values

        fee = provider._compute_stripe_fee(
            amount,
            currency,
            partner.country_id if partner else None
        )

        print("💰 Computed Fee:", fee)

        if fee <= 0:
            print("⚠ Fee = 0 -> SKIP")
            return tx_values

        is_international = provider._stripe_is_international(
            partner.country_id if partner else None
        )

        print("🌍 International:", is_international)

        tx_values.update({
            'amount': amount + fee,
            'stripe_fee_amount': fee,
            'stripe_fee_is_international': is_international,
        })

        print("✅ FINAL TX VALUES:", tx_values)

        return tx_values

    # =====================================================
    # STEP 2: CREATE FALLBACK
    # =====================================================
    @api.model_create_multi
    def create(self, vals_list):
        print("\n🔥 STEP 2: CREATE CALLED")
        print("Vals List:", vals_list)

        for vals in vals_list:
            provider = self.env['payment.provider'].sudo().browse(vals.get('provider_id'))

            print("\n--- Processing TX ---")
            print("Provider:", provider.code if provider else None)

            if not provider.exists() or provider.code != 'stripe' or not provider.stripe_add_extra_fees:
                print("❌ Not Stripe or fees disabled")
                continue

            amount = vals.get('amount')
            currency = self.env['res.currency'].browse(vals.get('currency_id'))
            partner = self.env['res.partner'].browse(vals.get('partner_id'))

            print("Amount:", amount)
            print("Currency:", currency.name if currency else None)

            if not amount or not currency:
                print("❌ Missing data")
                continue

            fee = provider._compute_stripe_fee(
                amount,
                currency,
                partner.country_id if partner else None
            )

            print("💰 Computed Fee (CREATE):", fee)

            if fee <= 0:
                print("⚠ Fee = 0")
                continue

            vals['stripe_fee_amount'] = fee
            vals['stripe_fee_is_international'] = provider._stripe_is_international(
                partner.country_id if partner else None
            )
            vals['amount'] = amount + fee

            print("✅ Updated vals:", vals)

        transactions = super().create(vals_list)

        print("✅ Transactions Created:", transactions.ids)

        transactions._stripe_sync_fee_amount()

        return transactions

    # =====================================================
    # STEP 3: WRITE
    # =====================================================
    def write(self, vals):
        print("\n🔥 STEP 3: WRITE CALLED")
        print("Vals:", vals)

        # 🚫 Prevent recursion loop
        if self.env.context.get('skip_stripe_fee_sync'):
            print("⛔ Skipping sync بسبب context flag")
            return super().write(vals)

        res = super().write(vals)

        tracked = {'provider_id', 'amount', 'currency_id', 'partner_id'}

        # ✅ Only trigger when relevant fields updated
        if tracked.intersection(vals.keys()):
            print("🔄 Sync Triggered")

            # ⚠️ IMPORTANT: pass context to avoid infinite loop
            self.with_context(skip_stripe_fee_sync=True)._stripe_sync_fee_amount()

        return res

    # =====================================================
    # STEP 4: SYNC
    # =====================================================
    def _stripe_sync_fee_amount(self):
        print("\n🔥 STEP 4: SYNC CALLED")

        for tx in self:
            print("\n--- Sync TX ---", tx.id)

            if tx.provider_code != 'stripe' or not tx.provider_id.stripe_add_extra_fees:
                print("❌ Not Stripe / disabled")
                continue

            base_amount = tx.amount - tx.stripe_fee_amount if tx.stripe_fee_amount else tx.amount

            print("Base Amount:", base_amount)

            fee = tx.provider_id._compute_stripe_fee(
                base_amount,
                tx.currency_id,
                tx.partner_id.country_id if tx.partner_id else None,
            )

            print("💰 Recomputed Fee:", fee)

            values = {
                'stripe_fee_amount': fee,
                'stripe_fee_is_international': tx.provider_id._stripe_is_international(
                    tx.partner_id.country_id if tx.partner_id else None
                ),
                'amount': base_amount + fee,
            }

            print("✅ Writing:", values)

            tx.with_context(skip_stripe_fee_sync=True).sudo().write(values)

    # =====================================================
    # STEP 5: AFTER PAYMENT
    # =====================================================
    def _reconcile_after_done(self):
        print("\n🔥 STEP 5: RECONCILE CALLED")

        res = super()._reconcile_after_done()

        for tx in self:
            print("TX:", tx.id, tx.state, tx.stripe_fee_amount)

        return res