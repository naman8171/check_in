# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    extra_fees = fields.Monetary(
        string="Stripe Extra Fees",
        currency_field='currency_id',
        compute='_compute_extra_fees',
        store=True,
        help="Surcharge collected on top of the base amount for this payment.",
    )
    base_amount = fields.Monetary(
        string="Base Amount",
        currency_field='currency_id',
        compute='_compute_extra_fees',
        store=True,
        help="Original amount before the Stripe surcharge was added.",
    )

    @api.depends('payment_transaction_id.extra_fees',
                 'payment_transaction_id.base_amount')
    def _compute_extra_fees(self):
        for rec in self:
            tx = rec.payment_transaction_id
            rec.extra_fees = tx.extra_fees if tx else 0.0
            rec.base_amount = tx.base_amount if tx else 0.0
