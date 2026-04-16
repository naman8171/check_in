# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    stripe_add_extra_fees = fields.Boolean(
        string='Add Extra Fees',
        default=False,
    )

    stripe_fee_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Stripe Fee Product',
        domain=[('type', '=', 'service')],
    )

    stripe_domestic_fixed_fee = fields.Float(string='Fixed Domestic Fees', default=0.0)
    stripe_domestic_variable_fee = fields.Float(string='Variable Domestic Fees (%)', default=0.0)
    stripe_domestic_free_above = fields.Boolean(string='Free Domestic Fees Above')
    stripe_domestic_total_amount = fields.Float(string='Domestic Threshold', default=0.0)

    stripe_international_fixed_fee = fields.Float(string='Fixed International Fees', default=0.0)
    stripe_international_variable_fee = fields.Float(string='Variable International Fees (%)', default=0.0)
    stripe_international_free_above = fields.Boolean(string='Free International Fees Above')
    stripe_international_total_amount = fields.Float(string='International Threshold', default=0.0)

    # ----------------------------
    # VALIDATIONS
    # ----------------------------

    @api.constrains('stripe_domestic_variable_fee', 'stripe_international_variable_fee')
    def _check_variable_fees(self):
        for provider in self:
            print("\n🔍 Checking Variable Fees")

            if provider.stripe_domestic_variable_fee < 0 or provider.stripe_domestic_variable_fee > 100:
                print("❌ Invalid Domestic % Fee")
                raise ValidationError(_('Variable domestic fee must be between 0 and 100%.'))

            if provider.stripe_international_variable_fee < 0 or provider.stripe_international_variable_fee > 100:
                print("❌ Invalid International % Fee")
                raise ValidationError(_('Variable international fee must be between 0 and 100%.'))

    @api.constrains('stripe_domestic_fixed_fee', 'stripe_international_fixed_fee')
    def _check_fixed_fees(self):
        for provider in self:
            print("\n🔍 Checking Fixed Fees")

            if provider.stripe_domestic_fixed_fee < 0:
                print("❌ Domestic Fixed Fee Negative")
                raise ValidationError(_('Fixed domestic fee cannot be negative.'))

            if provider.stripe_international_fixed_fee < 0:
                print("❌ International Fixed Fee Negative")
                raise ValidationError(_('Fixed international fee cannot be negative.'))

    # ----------------------------
    # ONCHANGE
    # ----------------------------

    @api.onchange('stripe_add_extra_fees')
    def _onchange_stripe_add_extra_fees(self):
        print("\n⚡ Onchange Triggered: stripe_add_extra_fees =", self.stripe_add_extra_fees)

        if self.stripe_add_extra_fees and not self.stripe_fee_product_id:
            print("🔍 Searching default fee product...")

            fee_product = self.env.ref(
                'payment_stripe_extra_fees.product_stripe_fee',
                raise_if_not_found=False
            )

            if fee_product:
                print("✅ Fee product found:", fee_product.name)
                self.stripe_fee_product_id = fee_product.product_variant_id
            else:
                print("❌ Fee product NOT found")

    # ----------------------------
    # MAIN LOGIC
    # ----------------------------

    def _compute_stripe_fee(self, amount, currency, partner_country=None):
        self.ensure_one()

        print("\n🔥 ===== STRIPE FEE CALCULATION START =====")

        print("Provider:", self.name)
        print("Amount:", amount)
        print("Currency:", currency.name if currency else None)

        print("Partner Country:", partner_country.name if partner_country else None)
        print("Company Country:", self.company_id.country_id.name if self.company_id.country_id else None)

        print("Extra Fees Enabled:", self.stripe_add_extra_fees)

        if not self.stripe_add_extra_fees:
            print("❌ Fees Disabled")
            return 0.0

        if amount <= 0:
            print("❌ Invalid Amount")
            return 0.0

        is_international = self._stripe_is_international(partner_country)
        print("🌍 Is International:", is_international)

        print("\n📊 CONFIG VALUES")
        print("Domestic Fixed:", self.stripe_domestic_fixed_fee)
        print("Domestic %:", self.stripe_domestic_variable_fee)
        print("Domestic Free Above:", self.stripe_domestic_free_above)
        print("Domestic Threshold:", self.stripe_domestic_total_amount)

        print("International Fixed:", self.stripe_international_fixed_fee)
        print("International %:", self.stripe_international_variable_fee)
        print("International Free Above:", self.stripe_international_free_above)
        print("International Threshold:", self.stripe_international_total_amount)

        if is_international:
            print("👉 USING INTERNATIONAL FEES")
            fixed_fee = self.stripe_international_fixed_fee
            variable_fee_pct = self.stripe_international_variable_fee
            free_above = self.stripe_international_free_above
            threshold = self.stripe_international_total_amount
        else:
            print("👉 USING DOMESTIC FEES")
            fixed_fee = self.stripe_domestic_fixed_fee
            variable_fee_pct = self.stripe_domestic_variable_fee
            free_above = self.stripe_domestic_free_above
            threshold = self.stripe_domestic_total_amount

        print("\n⚙️ Applied Values")
        print("Fixed Fee:", fixed_fee)
        print("Variable %:", variable_fee_pct)
        print("Free Above:", free_above)
        print("Threshold:", threshold)

        if free_above:
            print("🔍 Checking Threshold:", amount, ">=", threshold)

        if free_above and threshold > 0 and amount >= threshold:
            print("⚠ Fee WAIVED بسبب threshold")
            return 0.0

        variable_fee = amount * (variable_fee_pct / 100.0)
        print("🧮 Variable Fee:", variable_fee)

        total_fee = fixed_fee + variable_fee
        print("🧮 Total Fee Before Round:", total_fee)

        if currency:
            total_fee = currency.round(total_fee)
            print("🔄 Rounded Fee:", total_fee)

        print("✅ FINAL FEE:", total_fee)
        print("🔥 ===== STRIPE FEE CALCULATION END =====\n")

        return total_fee

    # ----------------------------
    # COUNTRY CHECK
    # ----------------------------

    def _stripe_is_international(self, partner_country=None):
        self.ensure_one()

        print("\n🌍 Checking International Logic")

        if not partner_country:
            print("⚠ No partner country → Domestic assumed")
            return False

        company_country = self.company_id.country_id

        if not company_country:
            print("⚠ No company country → Domestic assumed")
            return False

        print("Partner Country:", partner_country.name)
        print("Company Country:", company_country.name)

        result = partner_country.id != company_country.id

        print("👉 Is International Result:", result)

        return result