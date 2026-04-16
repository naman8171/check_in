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
    def stripe_fee_preview(self, provider_id=None, **kwargs):
        """
        Return a preview of the Stripe extra fee for the current cart.

        :param int provider_id: The payment provider ID.
        :return: dict with fee_amount and fee_formatted.
        """
        try:
            if not provider_id:
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            provider = request.env['payment.provider'].sudo().browse(int(provider_id))
            if not provider.exists() or provider.code != 'stripe':
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            if not provider.stripe_add_extra_fees:
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            # Get current cart / sale order
            sale_order = request.website.sale_get_order() if hasattr(request, 'website') else None
            if not sale_order:
                return {'fee_amount': 0.0, 'fee_formatted': '0.00'}

            amount = sale_order.amount_total
            currency = sale_order.currency_id
            partner = sale_order.partner_id

            fee = provider._compute_stripe_fee(amount, currency, partner.country_id)

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
        
    
