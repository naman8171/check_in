# -*- coding: utf-8 -*-

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class StripeFeeController(http.Controller):
    """
    Controller providing a fee preview endpoint for the frontend widget.
    Returns the computed Stripe extra fee for the current session's cart.
    """

    @http.route(
        '/payment/stripe/fee_preview',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False,
        website=True,
    )
    def stripe_fee_preview(self, provider_id=None, amount=None, currency_id=None, partner_id=None, **kwargs):
        """
        Return a preview of the Stripe extra fee for the current cart.

        :param int provider_id: The payment provider ID.
        :return: dict with fee_amount and fee_formatted.
        """
        try:
            provider = None
            if provider_id:
                provider = request.env['payment.provider'].sudo().browse(int(provider_id))
                if not provider.exists() or provider.code != 'stripe':
                    provider = None

            if not provider:
                website = getattr(request, 'website', False)
                company = website.company_id if website else request.env.company
                provider = request.env['payment.provider'].sudo().search([
                    ('code', '=', 'stripe'),
                    ('company_id', '=', company.id),
                    ('state', '!=', 'disabled'),
                ], limit=1)
                if not provider:
                    return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            if not provider.stripe_add_extra_fees:
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            currency = None
            partner = None
            base_amount = 0.0

            # 1) explicit data from frontend (invoice modal / custom forms)
            if amount is not None and currency_id:
                base_amount = float(amount)
                currency = request.env['res.currency'].sudo().browse(int(currency_id))
                partner = request.env['res.partner'].sudo().browse(int(partner_id)) if partner_id else request.env.user.partner_id

            # 2) website cart fallback (shop checkout)
            if not currency:
                sale_order = request.website.sale_get_order() if hasattr(request, 'website') else None
                if sale_order:
                    base_amount = sale_order.amount_total
                    currency = sale_order.currency_id
                    partner = sale_order.partner_id

            if not currency:
                website = getattr(request, 'website', False)
                company = website.company_id if website else request.env.company
                currency = company.currency_id
                partner = request.env.user.partner_id

            fee = provider._compute_stripe_fee(base_amount, currency, partner.country_id)

            if fee <= 0:
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            # Format fee with currency symbol
            fee_formatted = '{symbol}{amount:.2f}'.format(
                symbol=currency.symbol or '',
                amount=fee,
            )

            return {
                'fee_amount': fee,
                'fee_formatted': fee_formatted,
                'currency_symbol': currency.symbol or '',
                'is_international': provider._stripe_is_international(partner.country_id),
            }

        except Exception as e:
            _logger.warning('Stripe fee preview error: %s', str(e))
            return {'fee_amount': 0.0, 'fee_formatted': '0.00'}
        
    