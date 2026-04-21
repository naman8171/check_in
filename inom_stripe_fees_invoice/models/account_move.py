from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    stripe_base_amount = fields.Monetary(
        string='Base amount',
        currency_field='currency_id',
        compute='_compute_stripe_fee_breakdown',
        help='Invoice amount before Stripe processing fee.',
    )
    stripe_processing_fee = fields.Monetary(
        string='Stripe processing fee*',
        currency_field='currency_id',
        compute='_compute_stripe_fee_breakdown',
        help='Estimated Stripe surcharge based on current Stripe fee settings.',
    )
    stripe_total_to_be_charged = fields.Monetary(
        string='Total to be charged',
        currency_field='currency_id',
        compute='_compute_stripe_fee_breakdown',
        help='Amount that will be charged when paying this invoice with Stripe.',
    )

    @api.depends('move_type', 'state', 'amount_total', 'amount_residual', 'partner_id.country_id', 'company_id')
    def _compute_stripe_fee_breakdown(self):
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

            base_amount = 0.0
            fee = 0.0
            if is_customer_invoice:
                # Draft/proforma uses full total; posted uses outstanding amount (portal behavior).
                base_amount = move.amount_residual if move.state == 'posted' else move.amount_total
                if provider and base_amount > 0:
                    fee = provider._compute_custom_fees(base_amount, move.partner_id.country_id)

            move.stripe_base_amount = base_amount
            move.stripe_processing_fee = fee
            move.stripe_total_to_be_charged = base_amount + fee
