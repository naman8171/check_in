# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    stripe_add_extra_fees = fields.Boolean(
        string='Add Extra Fees',
        default=False,
        help='Enable to add extra processing fees on top of the order total for Stripe payments.',
    )
    stripe_fee_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Stripe Fee Product',
        domain=[('type', '=', 'service')],
        help='Product used to represent the Stripe fee on invoices and orders. '
             'Will be auto-created if left empty.',
    )
    stripe_domestic_fixed_fee = fields.Float(
        string='Fixed Domestic Fees',
        default=0.0,
        digits=(16, 2),
        help='Fixed fee amount applied to domestic transactions (same currency/country).',
    )
    stripe_domestic_variable_fee = fields.Float(
        string='Variable Domestic Fees (in percents)',
        default=0.0,
        digits=(16, 4),
        help='Percentage fee applied to domestic transactions. E.g., 1.5 means 1.5%.',
    )
    stripe_domestic_free_above = fields.Boolean(
        string='Free Domestic Fees if Total Amount is Above',
        default=False,
        help='If enabled, domestic fees are waived when the order total exceeds the threshold.',
    )
    stripe_domestic_total_amount = fields.Float(
        string='Domestic Total Amount',
        default=0.0,
        digits=(16, 2),
        help='Minimum order amount above which domestic fees are waived.',
    )
    stripe_international_fixed_fee = fields.Float(
        string='Fixed International Fees',
        default=0.0,
        digits=(16, 2),
        help='Fixed fee amount applied to international transactions (cross-border).',
    )
    stripe_international_variable_fee = fields.Float(
        string='Variable International Fees (in percents)',
        default=0.0,
        digits=(16, 4),
        help='Percentage fee applied to international transactions. E.g., 1.5 means 1.5%.',
    )
    stripe_international_free_above = fields.Boolean(
        string='Free International Fees if Total Amount is Above',
        default=False,
        help='If enabled, international fees are waived when the order total exceeds the threshold.',
    )
    stripe_international_total_amount = fields.Float(
        string='International Total Amount',
        default=0.0,
        digits=(16, 2),
        help='Minimum order amount above which international fees are waived.',
    )

    @api.constrains('stripe_domestic_variable_fee', 'stripe_international_variable_fee')
    def _check_variable_fees(self):
        print("DEBUG: _check_variable_fees called")
        for provider in self:
            print("DEBUG provider variable fees:", provider.stripe_domestic_variable_fee, provider.stripe_international_variable_fee)

            if provider.stripe_domestic_variable_fee < 0 or provider.stripe_domestic_variable_fee > 100:
                print("ERROR: domestic variable fee invalid")
                raise ValidationError(_('Variable domestic fee must be between 0 and 100%.'))

            if provider.stripe_international_variable_fee < 0 or provider.stripe_international_variable_fee > 100:
                print("ERROR: international variable fee invalid")
                raise ValidationError(_('Variable international fee must be between 0 and 100%.'))

    @api.constrains('stripe_domestic_fixed_fee', 'stripe_international_fixed_fee')
    def _check_fixed_fees(self):
        print("DEBUG: _check_fixed_fees called")
        for provider in self:
            print("DEBUG provider fixed fees:", provider.stripe_domestic_fixed_fee, provider.stripe_international_fixed_fee)

            if provider.stripe_domestic_fixed_fee < 0:
                print("ERROR: domestic fixed fee negative")
                raise ValidationError(_('Fixed domestic fee cannot be negative.'))

            if provider.stripe_international_fixed_fee < 0:
                print("ERROR: international fixed fee negative")
                raise ValidationError(_('Fixed international fee cannot be negative.'))

    @api.onchange('stripe_add_extra_fees')
    def _onchange_stripe_add_extra_fees(self):
        print("DEBUG: onchange stripe_add_extra_fees triggered")
        print("Value:", self.stripe_add_extra_fees)

        if self.stripe_add_extra_fees and not self.stripe_fee_product_id:
            print("DEBUG: trying to auto assign fee product")

            fee_product = self.env.ref(
                'payment_stripe_extra_fees.product_stripe_fee',
                raise_if_not_found=False
            )

            print("DEBUG fee product found:", fee_product)

            if fee_product:
                self.stripe_fee_product_id = fee_product
                print("DEBUG: fee product assigned")

    def _compute_stripe_fee(self, amount, currency, partner_country=None):
        self.ensure_one()

        print("\n================ STRIPE FEE DEBUG START ================")
        print("Amount:", amount)
        print("Currency:", currency.name if currency else None)
        print("Partner Country:", partner_country.name if partner_country else None)
        print("Provider:", self.name)
        print("Extra Fees Enabled:", self.stripe_add_extra_fees)

        if not self.stripe_add_extra_fees:
            print("DEBUG STOP: extra fees disabled")
            return 0.0

        if amount <= 0:
            print("DEBUG STOP: invalid amount")
            return 0.0

        is_international = self._stripe_is_international(partner_country)
        print("Is International:", is_international)

        if is_international:
            print("DEBUG: using international config")
            fixed_fee = self.stripe_international_fixed_fee
            variable_fee_pct = self.stripe_international_variable_fee
            free_above = self.stripe_international_free_above
            threshold = self.stripe_international_total_amount
        else:
            print("DEBUG: using domestic config")
            fixed_fee = self.stripe_domestic_fixed_fee
            variable_fee_pct = self.stripe_domestic_variable_fee
            free_above = self.stripe_domestic_free_above
            threshold = self.stripe_domestic_total_amount

        print("Fixed Fee:", fixed_fee)
        print("Variable Fee %:", variable_fee_pct)
        print("Free Above:", free_above)
        print("Threshold:", threshold)

        if free_above and threshold > 0 and amount >= threshold:
            print("DEBUG STOP: free above condition matched")
            return 0.0

        variable_fee = amount * (variable_fee_pct / 100.0)
        total_fee = fixed_fee + variable_fee

        print("Calculated variable fee:", variable_fee)
        print("Total fee before rounding:", total_fee)

        if currency:
            total_fee = currency.round(total_fee)
            print("Rounded fee:", total_fee)

        print("FINAL FEE:", total_fee)
        print("================ STRIPE FEE DEBUG END ================\n")

        return total_fee

    def _stripe_is_international(self, partner_country=None):
        self.ensure_one()

        print("DEBUG: checking international transaction")

        if not partner_country:
            print("DEBUG: no partner country -> domestic")
            return False

        company_country = self.company_id.country_id

        print("Company Country:", company_country.name if company_country else None)
        print("Partner Country:", partner_country.name)

        if not company_country:
            print("DEBUG: no company country -> domestic")
            return False

        result = partner_country.id != company_country.id
        print("DEBUG international result:", result)
        return result

    def _get_compatible_providers(self, *args, **kwargs):
        print("DEBUG: _get_compatible_providers called")
        return super()._get_compatible_providers(*args, **kwargs)