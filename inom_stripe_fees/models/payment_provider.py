# -*- coding: utf-8 -*-
from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    fees_custom_active = fields.Boolean(
        string="Enable Custom Fees",
        help="Add extra fees on top of the transaction amount for this provider.",
    )
    fees_dom_var = fields.Float(
        string="Domestic Fees (%)",
        default=0.0,
        help="Variable domestic fee, as a percentage of the transaction amount.",
    )
    fees_dom_fixed = fields.Float(
        string="Domestic Fixed Fee",
        default=0.0,
        help="Flat fee added to all domestic transactions (in the company currency).",
    )
    fees_int_var = fields.Float(
        string="International Fees (%)",
        default=0.0,
        help="Variable international fee, as a percentage of the transaction amount.",
    )
    fees_int_fixed = fields.Float(
        string="International Fixed Fee",
        default=0.0,
        help="Flat fee added to all international transactions (in the company currency).",
    )
    fees_free_limit = fields.Float(
        string="Waive Fees Above",
        default=0.0,
        help="If the base transaction amount is strictly greater than this limit, "
             "no extra fee is charged. Leave at 0 to always charge the fee.",
    )

    def _compute_custom_fees(self, amount, partner_country):
        """Return the surcharge to add on top of `amount`.

        :param float amount: the base transaction amount.
        :param res.country partner_country: the customer's country (usually the
               delivery country; falls back to billing).
        :return: float — the fee amount, rounded to 2 decimals.
        """
        self.ensure_one()
        if not self.fees_custom_active or amount <= 0:
            return 0.0
        # Waive fees for large orders if a threshold is configured.
        if self.fees_free_limit and amount > self.fees_free_limit:
            return 0.0

        company_country = self.company_id.country_id
        is_domestic = bool(
            partner_country
            and company_country
            and partner_country.id == company_country.id
        )
        if is_domestic:
            variable = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            variable = self.fees_int_var
            fixed = self.fees_int_fixed

        fee = (amount * variable / 100.0) + fixed
        return round(fee, 2)
