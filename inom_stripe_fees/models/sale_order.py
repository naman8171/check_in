# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_stripe_fee_line = fields.Boolean(
        string="Stripe Fee Line",
        default=False,
        help="Technical flag for the extra Stripe processing fee line.",
    )
