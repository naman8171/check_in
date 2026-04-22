# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    stripe_fee_amount = fields.Monetary(
        string='Stripe Fee',
        currency_field='currency_id',
        compute='_compute_stripe_fee_amount',
        store=True,
        readonly=True,
        help='Stripe fee collected from successful Stripe payment transactions for this invoice.',
    )

    @api.depends('transaction_ids.state', 'transaction_ids.provider_code', 'transaction_ids.stripe_fee_amount')
    def _compute_stripe_fee_amount(self):
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                move.stripe_fee_amount = 0.0
                continue

            move.stripe_fee_amount = sum(
                tx.stripe_fee_amount
                for tx in move.transaction_ids
                if tx.provider_code == 'stripe' and tx.state in ('done', 'authorized')
            )
