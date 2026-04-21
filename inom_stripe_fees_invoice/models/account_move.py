from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    stripe_fee_estimated = fields.Monetary(
        string='Stripe Extra Fee (Estimated)',
        currency_field='currency_id',
        compute='_compute_stripe_fee_amounts',
        help='Estimated Stripe surcharge based on the current Stripe provider configuration.',
    )
    stripe_fee_paid = fields.Monetary(
        string='Stripe Extra Fee (Paid)',
        currency_field='currency_id',
        compute='_compute_stripe_fee_amounts',
        store=True,
        help='Actual Stripe surcharge collected from completed Stripe payment transactions.',
    )
    stripe_total_with_fee = fields.Monetary(
        string='Total with Stripe Fee',
        currency_field='currency_id',
        compute='_compute_stripe_fee_amounts',
        help='Invoice total plus the estimated Stripe surcharge.',
    )

    @api.depends(
        'move_type',
        'state',
        'amount_total',
        'partner_id.country_id',
        'company_id',
        'transaction_ids.extra_fees',
        'transaction_ids.state',
        'transaction_ids.provider_id',
    )
    def _compute_stripe_fee_amounts(self):
        providers_by_company = {
            company.id: self.env['payment.provider'].search([
                ('code', '=', 'stripe'),
                ('company_id', '=', company.id),
                ('state', 'in', ('enabled', 'test')),
                ('fees_custom_active', '=', True),
            ], limit=1)
            for company in self.mapped('company_id')
        }

        for move in self:
            is_customer_invoice = move.move_type in ('out_invoice', 'out_refund')
            provider = providers_by_company.get(move.company_id.id)

            if is_customer_invoice and provider and move.state == 'posted':
                move.stripe_fee_estimated = provider._compute_custom_fees(
                    move.amount_total,
                    move.partner_id.country_id,
                )
            else:
                move.stripe_fee_estimated = 0.0

            done_stripe_transactions = move.transaction_ids.filtered(
                lambda tx: tx.provider_id.code == 'stripe' and tx.state == 'done'
            )
            move.stripe_fee_paid = sum(done_stripe_transactions.mapped('extra_fees'))
            move.stripe_total_with_fee = move.amount_total + move.stripe_fee_estimated
