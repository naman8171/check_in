# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import time
from functools import wraps

from odoo import fields, http, _
from odoo.exceptions import AccessDenied
from odoo.http import Response, request


class MobileCommerceApiController(http.Controller):
    API_PREFIX = '/mobile/api/v1'

    def _json_response(self, payload, status=200):
        body = json.dumps(payload, default=str)
        return Response(body, status=status, content_type='application/json; charset=utf-8')

    def _payload(self):
        raw = request.httprequest.get_data(as_text=True) or '{}'
        if not raw:
            return {}
        return json.loads(raw)

    def _b64url_encode(self, value):
        return base64.urlsafe_b64encode(value).rstrip(b'=').decode()

    def _b64url_decode(self, value):
        padding = '=' * (-len(value) % 4)
        return base64.urlsafe_b64decode((value + padding).encode())

    def _jwt_encode(self, payload, secret):
        header = {'alg': 'HS256', 'typ': 'JWT'}
        header_b64 = self._b64url_encode(json.dumps(header, separators=(',', ':')).encode())
        payload_b64 = self._b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
        message = '%s.%s' % (header_b64, payload_b64)
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
        return '%s.%s' % (message, self._b64url_encode(signature))

    def _jwt_decode(self, token, secret):
        try:
            header_b64, payload_b64, signature_b64 = token.split('.')
            message = '%s.%s' % (header_b64, payload_b64)
            expected = self._b64url_encode(hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest())
            if not hmac.compare_digest(expected, signature_b64):
                return {}
            payload = json.loads(self._b64url_decode(payload_b64).decode())
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
        if payload.get('exp') and payload['exp'] < int(time.time()):
            return {}
        return payload

    def _endpoint(self):
        return request.httprequest.path

    def _get_api_key(self):
        api_key = request.httprequest.headers.get('X-Mobile-Api-Key') or request.params.get('api_key')
        return request.env['mobile.api.key'].sudo().authenticate(api_key)

    def _get_context(self, require_user=False):
        api_key = self._get_api_key()
        if not api_key:
            return None, self._json_response({'success': False, 'error': 'invalid_api_key'}, status=401)
        app_config = api_key.app_config_id
        if app_config.maintenance_mode:
            return None, self._json_response({'success': False, 'error': 'maintenance_mode', 'message': app_config.maintenance_message}, status=503)
        user = request.env['res.users'].sudo().browse()
        auth_header = request.httprequest.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            payload = self._jwt_decode(token, app_config.jwt_secret or '',)
            if payload.get('uid') and payload.get('app') == app_config.id:
                user = request.env['res.users'].sudo().browse(int(payload['uid'])).exists()
        if require_user and not user:
            return None, self._json_response({'success': False, 'error': 'authentication_required'}, status=401)
        return {'api_key': api_key, 'app_config': app_config, 'user': user}, None

    def _log(self, ctx, payload, response_payload, status=200, started_at=None, error=None):
        duration_ms = int((time.time() - started_at) * 1000) if started_at else 0
        app_config = ctx.get('app_config') if ctx else False
        api_key = ctx.get('api_key') if ctx else False
        user = ctx.get('user') if ctx else request.env['res.users']
        partner = user.partner_id if user else False
        request.env['mobile.api.log'].sudo().create({
            'app_config_id': app_config.id if app_config else False,
            'api_key_id': api_key.id if api_key else False,
            'user_id': user.id if user else False,
            'partner_id': partner.id if partner else False,
            'company_id': app_config.company_id.id if app_config else False,
            'website_id': app_config.website_id.id if app_config else False,
            'endpoint': self._endpoint(),
            'method': request.httprequest.method,
            'ip_address': request.httprequest.remote_addr,
            'request_payload': json.dumps(payload, default=str)[:10000],
            'response_payload': json.dumps(response_payload, default=str)[:10000],
            'status_code': status,
            'duration_ms': duration_ms,
            'error_message': error,
        })

    def _product_payload(self, product, website, pricelist=None):
        website_currency = getattr(website, 'currency_id', False)
        currency = (pricelist.currency_id if pricelist else website_currency) or product.currency_id
        return {
            'id': product.id,
            'name': product.name,
            'default_code': product.default_code,
            'description': product.description_sale or product.description or '',
            'price': product.list_price,
            'currency': {'id': currency.id, 'name': currency.name, 'symbol': currency.symbol},
            'image_url': '/web/image/product.template/%s/image_1024' % product.id,
            'category_ids': product.public_categ_ids.ids,
            'variant_count': len(product.product_variant_ids),
            'variants': [{'id': item.id, 'name': item.display_name, 'default_code': item.default_code} for item in product.product_variant_ids],
            'website_url': product.website_url,
        }

    def _auth_required(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            started_at = time.time()
            payload = self._payload() if request.httprequest.method in ('POST', 'PUT', 'PATCH') else dict(request.params)
            ctx, error_response = self._get_context(require_user=True)
            if error_response:
                return error_response
            try:
                response_payload = func(self, ctx, payload, *args, **kwargs)
                self._log(ctx, payload, response_payload, started_at=started_at)
                return self._json_response(response_payload)
            except Exception as exc:
                response_payload = {'success': False, 'error': str(exc)}
                self._log(ctx, payload, response_payload, status=500, started_at=started_at, error=str(exc))
                return self._json_response(response_payload, status=500)
        return wrapper

    def _public_api(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            started_at = time.time()
            payload = self._payload() if request.httprequest.method in ('POST', 'PUT', 'PATCH') else dict(request.params)
            ctx, error_response = self._get_context(require_user=False)
            if error_response:
                return error_response
            try:
                response_payload = func(self, ctx, payload, *args, **kwargs)
                self._log(ctx, payload, response_payload, started_at=started_at)
                return self._json_response(response_payload)
            except Exception as exc:
                response_payload = {'success': False, 'error': str(exc)}
                self._log(ctx, payload, response_payload, status=500, started_at=started_at, error=str(exc))
                return self._json_response(response_payload, status=500)
        return wrapper

    @http.route(API_PREFIX + '/config', type='http', auth='public', methods=['GET'], csrf=False)
    @_public_api
    def config(self, ctx, payload):
        app = ctx['app_config']
        return {'success': True, 'data': {
            'app_name': app.name,
            'logo_url': '/web/image/mobile.app.config/%s/logo' % app.id,
            'splash_url': '/web/image/mobile.app.config/%s/splash_screen' % app.id,
            'colors': {'primary': app.primary_color, 'secondary': app.secondary_color, 'accent': app.accent_color},
            'firebase': {'project_id': app.firebase_project_id, 'sender_id': app.firebase_sender_id},
            'features': {'guest_checkout': app.allow_guest_checkout, 'wishlist': app.enable_wishlist, 'reviews': app.enable_product_reviews, 'comparison': app.enable_product_comparison},
            'website': {'id': app.website_id.id, 'name': app.website_id.name},
            'currency': {'id': app.currency_id.id, 'name': app.currency_id.name, 'symbol': app.currency_id.symbol},
            'languages': [{'code': lang.code, 'name': lang.name} for lang in app.language_ids],
        }}

    @http.route(API_PREFIX + '/auth/register', type='http', auth='public', methods=['POST'], csrf=False)
    @_public_api
    def register(self, ctx, payload):
        name = payload.get('name')
        email = payload.get('email')
        password = payload.get('password')
        if not name or not email or not password:
            return {'success': False, 'error': 'name_email_password_required'}
        existing = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing:
            return {'success': False, 'error': 'email_already_registered'}
        group_portal = request.env.ref('base.group_portal')
        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
            'groups_id': [(6, 0, [group_portal.id])],
            'company_id': ctx['app_config'].company_id.id,
            'company_ids': [(4, ctx['app_config'].company_id.id)],
        })
        return self._login_response(ctx, user)

    @http.route(API_PREFIX + '/auth/login', type='http', auth='public', methods=['POST'], csrf=False)
    @_public_api
    def login(self, ctx, payload):
        login = payload.get('login') or payload.get('email')
        password = payload.get('password')
        try:
            try:
                uid = request.session.authenticate(request.db, login, password)
            except TypeError:
                uid = request.session.authenticate(request.db, {'login': login, 'password': password, 'type': 'password'})
        except AccessDenied:
            return {'success': False, 'error': 'invalid_login'}
        user = request.env['res.users'].sudo().browse(uid)
        return self._login_response(ctx, user)

    def _login_response(self, ctx, user):
        app = ctx['app_config']
        now = int(time.time())
        exp = now + (app.jwt_expiry_minutes * 60)
        token = self._jwt_encode({'uid': user.id, 'iat': now, 'exp': exp, 'app': app.id}, app.jwt_secret or '')
        return {'success': True, 'token': token, 'expires_at': exp, 'customer': self._partner_payload(user.partner_id)}

    @http.route(API_PREFIX + '/auth/logout', type='http', auth='public', methods=['POST'], csrf=False)
    @_auth_required
    def logout(self, ctx, payload):
        request.session.logout(keep_db=True)
        return {'success': True}

    @http.route(API_PREFIX + '/auth/forgot-password', type='http', auth='public', methods=['POST'], csrf=False)
    @_public_api
    def forgot_password(self, ctx, payload):
        login = payload.get('login') or payload.get('email')
        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if user:
            user.action_reset_password()
        return {'success': True, 'message': _('If the account exists, reset instructions have been sent.')}

    def _partner_payload(self, partner):
        return {'id': partner.id, 'name': partner.name, 'email': partner.email, 'phone': partner.phone, 'mobile': partner.mobile}

    @http.route(API_PREFIX + '/customer/profile', type='http', auth='public', methods=['GET', 'PUT'], csrf=False)
    @_auth_required
    def profile(self, ctx, payload):
        partner = ctx['user'].partner_id
        if request.httprequest.method == 'PUT':
            vals = {key: payload[key] for key in ('name', 'phone', 'mobile', 'street', 'street2', 'city', 'zip') if key in payload}
            partner.sudo().write(vals)
        return {'success': True, 'data': self._partner_payload(partner)}

    @http.route(API_PREFIX + '/customer/addresses', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    @_auth_required
    def addresses(self, ctx, payload):
        partner = ctx['user'].partner_id
        if request.httprequest.method == 'POST':
            vals = {key: payload.get(key) for key in ('name', 'phone', 'street', 'street2', 'city', 'zip') if payload.get(key)}
            vals.update({'parent_id': partner.id, 'type': payload.get('type', 'delivery')})
            partner.sudo().create(vals)
        addresses = partner.child_ids | partner
        return {'success': True, 'data': [{'id': item.id, 'name': item.name, 'type': item.type, 'street': item.street, 'city': item.city, 'zip': item.zip} for item in addresses]}

    @http.route(API_PREFIX + '/products', type='http', auth='public', methods=['GET'], csrf=False)
    @_public_api
    def products(self, ctx, payload):
        website = ctx['app_config'].website_id
        domain = [('sale_ok', '=', True), ('is_published', '=', True)]
        if payload.get('search'):
            domain.append(('name', 'ilike', payload['search']))
        if payload.get('category_id'):
            domain.append(('public_categ_ids', 'child_of', int(payload['category_id'])))
        limit = int(payload.get('limit', 20))
        offset = int(payload.get('offset', 0))
        products = request.env['product.template'].sudo().with_context(website_id=website.id).search(domain, limit=limit, offset=offset)
        return {'success': True, 'data': [self._product_payload(product, website) for product in products], 'count': len(products)}

    @http.route(API_PREFIX + '/products/<int:product_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @_public_api
    def product_detail(self, ctx, payload, product_id):
        website = ctx['app_config'].website_id
        product = request.env['product.template'].sudo().browse(product_id).exists()
        if not product or not product.sale_ok or not product.is_published:
            return {'success': False, 'error': 'product_not_found'}
        reviews = request.env['mobile.product.review'].sudo().search([('product_tmpl_id', '=', product.id), ('state', '=', 'approved')], limit=20)
        data = self._product_payload(product, website)
        data.update({
            'images': ['/web/image/product.template/%s/image_1920' % product.id],
            'reviews': [{'rating': item.rating, 'name': item.name, 'comment': item.comment} for item in reviews],
            'related_products': [self._product_payload(item, website) for item in product.alternative_product_ids[:8]] if hasattr(product, 'alternative_product_ids') else [],
        })
        return {'success': True, 'data': data}

    @http.route(API_PREFIX + '/categories', type='http', auth='public', methods=['GET'], csrf=False)
    @_public_api
    def categories(self, ctx, payload):
        categories = request.env['product.public.category'].sudo().search([])
        def node(category):
            children = categories.filtered(lambda item: item.parent_id == category)
            return {'id': category.id, 'name': category.name, 'image_url': '/web/image/product.public.category/%s/image_1920' % category.id, 'children': [node(child) for child in children]}
        roots = categories.filtered(lambda item: not item.parent_id)
        return {'success': True, 'data': [node(category) for category in roots]}

    @http.route(API_PREFIX + '/home', type='http', auth='public', methods=['GET'], csrf=False)
    @_public_api
    def home(self, ctx, payload):
        app = ctx['app_config']
        banners = request.env['mobile.banner'].sudo().search([('app_config_id', '=', app.id), ('active', '=', True)], order='sequence,id')
        sliders = request.env['mobile.slider'].sudo().search([('app_config_id', '=', app.id), ('active', '=', True)], order='sequence,id')
        sections = request.env['mobile.home.section'].sudo().search([('app_config_id', '=', app.id), ('active', '=', True)], order='sequence,id')
        return {'success': True, 'data': {
            'banners': [{'id': item.id, 'title': item.title, 'image_url': '/web/image/mobile.banner/%s/image' % item.id, 'url': item.url} for item in banners],
            'sliders': [{'id': item.id, 'title': item.title, 'image_url': '/web/image/mobile.slider/%s/image' % item.id, 'url': item.cta_url} for item in sliders],
            'sections': [{'id': item.id, 'name': item.name, 'type': item.section_type, 'products': [self._product_payload(product, app.website_id) for product in item.product_tmpl_ids[:item.limit]]} for item in sections],
        }}

    def _sale_order(self, ctx, force_create=False):
        partner = ctx['user'].partner_id if ctx.get('user') else request.env.user.partner_id
        website = ctx['app_config'].website_id
        order = request.env['sale.order'].sudo().search([('partner_id', '=', partner.id), ('website_id', '=', website.id), ('state', '=', 'draft')], limit=1)
        if not order and force_create:
            order = request.env['sale.order'].sudo().create({'partner_id': partner.id, 'website_id': website.id, 'company_id': ctx['app_config'].company_id.id})
        return order

    @http.route(API_PREFIX + '/cart', type='http', auth='public', methods=['GET', 'POST', 'PUT', 'DELETE'], csrf=False)
    @_auth_required
    def cart(self, ctx, payload):
        order = self._sale_order(ctx, force_create=request.httprequest.method in ('POST', 'PUT'))
        if request.httprequest.method in ('POST', 'PUT'):
            product_id = int(payload.get('product_id'))
            quantity = float(payload.get('quantity', 1))
            order._cart_update(product_id=product_id, add_qty=quantity if request.httprequest.method == 'POST' else 0, set_qty=quantity if request.httprequest.method == 'PUT' else 0)
        if request.httprequest.method == 'DELETE' and payload.get('line_id'):
            order.order_line.filtered(lambda line: line.id == int(payload['line_id'])).unlink()
        lines = [{'id': line.id, 'product_id': line.product_id.id, 'name': line.name, 'quantity': line.product_uom_qty, 'price_unit': line.price_unit, 'subtotal': line.price_subtotal} for line in order.order_line] if order else []
        return {'success': True, 'data': {'order_id': order.id if order else False, 'lines': lines, 'amount_total': order.amount_total if order else 0}}

    @http.route(API_PREFIX + '/checkout/confirm', type='http', auth='public', methods=['POST'], csrf=False)
    @_auth_required
    def checkout_confirm(self, ctx, payload):
        order = self._sale_order(ctx)
        if not order:
            return {'success': False, 'error': 'empty_cart'}
        order.action_confirm()
        return {'success': True, 'data': {'order_id': order.id, 'name': order.name, 'amount_total': order.amount_total, 'state': order.state}}

    @http.route(API_PREFIX + '/orders', type='http', auth='public', methods=['GET'], csrf=False)
    @_auth_required
    def orders(self, ctx, payload):
        orders = request.env['sale.order'].sudo().search([('partner_id', '=', ctx['user'].partner_id.id)], limit=int(payload.get('limit', 20)))
        return {'success': True, 'data': [{'id': order.id, 'name': order.name, 'date_order': order.date_order, 'state': order.state, 'amount_total': order.amount_total} for order in orders]}

    @http.route(API_PREFIX + '/orders/<int:order_id>', type='http', auth='public', methods=['GET'], csrf=False)
    @_auth_required
    def order_detail(self, ctx, payload, order_id):
        order = request.env['sale.order'].sudo().browse(order_id).exists()
        if not order:
            return {'success': False, 'error': 'order_not_found'}
        if order.partner_id.commercial_partner_id != ctx['user'].partner_id.commercial_partner_id:
            return {'success': False, 'error': 'access_denied'}
        invoices = order.invoice_ids
        pickings = order.picking_ids
        return {'success': True, 'data': {
            'id': order.id,
            'name': order.name,
            'state': order.state,
            'amount_total': order.amount_total,
            'invoice_urls': ['/my/invoices/%s?download=true' % invoice.id for invoice in invoices],
            'deliveries': [{'id': picking.id, 'name': picking.name, 'state': picking.state, 'carrier_tracking_ref': getattr(picking, 'carrier_tracking_ref', False)} for picking in pickings],
        }}

    @http.route(API_PREFIX + '/wishlist', type='http', auth='public', methods=['GET', 'POST', 'DELETE'], csrf=False)
    @_auth_required
    def wishlist(self, ctx, payload):
        model = request.env['mobile.wishlist'].sudo()
        partner = ctx['user'].partner_id
        if request.httprequest.method == 'POST':
            model.create({'partner_id': partner.id, 'product_tmpl_id': int(payload['product_tmpl_id']), 'website_id': ctx['app_config'].website_id.id, 'company_id': ctx['app_config'].company_id.id})
        if request.httprequest.method == 'DELETE' and payload.get('product_tmpl_id'):
            model.search([('partner_id', '=', partner.id), ('product_tmpl_id', '=', int(payload['product_tmpl_id']))]).unlink()
        items = model.search([('partner_id', '=', partner.id), ('website_id', '=', ctx['app_config'].website_id.id)])
        return {'success': True, 'data': [self._product_payload(item.product_tmpl_id, ctx['app_config'].website_id) for item in items]}

    @http.route(API_PREFIX + '/devices/register', type='http', auth='public', methods=['POST'], csrf=False)
    @_public_api
    def register_device(self, ctx, payload):
        if not payload.get('platform') or not payload.get('device_uuid') or not payload.get('fcm_token'):
            return {'success': False, 'error': 'platform_device_uuid_fcm_token_required'}
        values = {
            'name': payload.get('name') or payload.get('device_uuid'),
            'app_config_id': ctx['app_config'].id,
            'platform': payload.get('platform'),
            'device_uuid': payload.get('device_uuid'),
            'fcm_token': payload.get('fcm_token'),
            'app_version': payload.get('app_version'),
            'os_version': payload.get('os_version'),
            'language': payload.get('language'),
        }
        device = request.env['mobile.device'].sudo().search([('app_config_id', '=', ctx['app_config'].id), ('device_uuid', '=', payload.get('device_uuid'))], limit=1)
        if device:
            device.write(values)
        else:
            device = request.env['mobile.device'].sudo().create(values)
        return {'success': True, 'data': {'id': device.id}}
