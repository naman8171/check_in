# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools import consteq


class InomStripeFeesController(http.Controller):
    """Expose the Stripe provider's fee configuration to the payment form
    so the frontend can show a live fee breakdown."""

    @http.route(
        '/inom_stripe_fees/config',
        type='json',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=False,
    )
    def get_fees_config(self, order_id=None, invoice_id=None,
                        access_token=None, **kwargs):
        """Return fee settings for the current context.

        Resolves the customer (and therefore the country used for
        domestic/international classification) from the URL's sale-order
        or invoice FIRST — so payments made via portal email links
        (without login) still classify correctly. Only falls back to
        request.env.user.partner_id when no document context is given.
        """
        provider = request.env['payment.provider'].sudo().search([
            ('code', '=', 'stripe'),
            ('state', 'in', ('enabled', 'test')),
            ('fees_custom_active', '=', True),
        ], limit=1)
        if not provider:
            return {'active': False}

        if access_token and isinstance(access_token, str):
            access_token = access_token.strip()

        partner = self._resolve_partner(order_id, invoice_id, access_token)
        company_country = provider.company_id.country_id
        partner_country = partner.country_id if partner else False

        is_domestic = bool(
            partner_country
            and company_country
            and partner_country.id == company_country.id
        )

        currency = provider.company_id.currency_id
        return {
            'active': True,
            'is_domestic': is_domestic,
            'pct': provider.fees_dom_var if is_domestic else provider.fees_int_var,
            'fixed': provider.fees_dom_fixed if is_domestic else provider.fees_int_fixed,
            'free_limit': provider.fees_free_limit,
            'currency_symbol': currency.symbol or '',
            'currency_position': currency.position or 'before',
            'currency_name': currency.name or '',
        }
    def _resolve_partner(self, order_id, invoice_id, access_token):
        """Partner lookup priority:
          1. sale.order matched by (order_id, access_token)
          2. account.move matched by (invoice_id, access_token)
          3. Website cart's partner
          4. Logged-in user's partner (original behaviour)
        """
        if order_id:
            order = self._get_document('sale.order', order_id, access_token)
            if order:
                return (
                    order.partner_shipping_id
                    or order.partner_invoice_id
                    or order.partner_id
                )
        if invoice_id:
            invoice = self._get_document('account.move', invoice_id, access_token)
            if invoice:
                return invoice.partner_id
        try:
            website = request.website
            if website:
                cart = website.sale_get_order()
                if cart and cart.partner_id:
                    return cart.partner_shipping_id or cart.partner_id
        except Exception:
            pass
        user = request.env.user
        if user and user.partner_id:
            return user.partner_id
        return False

    def _get_document(self, model_name, doc_id, access_token):
        """Look up a portal document by ID + access_token.

        Returns the record (sudo'd) if:
          - the provided access_token matches the stored token, OR
          - the logged-in user has legitimate read access.
        Otherwise returns None.
        """
        try:
            doc_id = int(doc_id)
        except (TypeError, ValueError):
            return None

        doc = request.env[model_name].sudo().browse(doc_id)
        if not doc.exists():
            return None

        stored_token = doc.access_token or ''
        if access_token and stored_token and consteq(stored_token, access_token):
            return doc
        try:
            doc_user = request.env[model_name].browse(doc_id)
            doc_user.check_access_rights('read')
            doc_user.check_access_rule('read')
            return doc
        except Exception:
            return None
