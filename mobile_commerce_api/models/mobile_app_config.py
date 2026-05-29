# -*- coding: utf-8 -*-
import secrets

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MobileAppConfig(models.Model):
    _name = 'mobile.app.config'
    _description = 'Mobile App Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='App Name', required=True, translate=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    website_id = fields.Many2one('website', string='Website', required=True, index=True)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=True, readonly=True)
    language_ids = fields.Many2many('res.lang', string='Supported Languages')
    logo = fields.Image(string='App Logo', max_width=1024, max_height=1024)
    splash_screen = fields.Image(string='Splash Screen', max_width=2048, max_height=2048)
    primary_color = fields.Char(default='#111827', required=True)
    secondary_color = fields.Char(default='#2563EB', required=True)
    accent_color = fields.Char(default='#F59E0B')
    firebase_project_id = fields.Char(groups='mobile_commerce_api.group_mobile_admin')
    firebase_sender_id = fields.Char(groups='mobile_commerce_api.group_mobile_admin')
    firebase_server_key = fields.Char(groups='mobile_commerce_api.group_mobile_admin')
    firebase_service_account_json = fields.Text(groups='mobile_commerce_api.group_mobile_admin')
    jwt_secret = fields.Char(string='JWT Signing Secret', groups='mobile_commerce_api.group_mobile_admin')
    jwt_expiry_minutes = fields.Integer(default=1440, required=True)
    api_rate_limit = fields.Integer(string='Requests / Minute / API Key', default=120, required=True)
    allow_guest_checkout = fields.Boolean(default=True)
    enable_push_notifications = fields.Boolean(default=True)
    enable_product_reviews = fields.Boolean(default=True)
    enable_product_comparison = fields.Boolean(default=True)
    enable_wishlist = fields.Boolean(default=True)
    maintenance_mode = fields.Boolean(tracking=True)
    maintenance_message = fields.Char(translate=True)
    terms_url = fields.Char()
    privacy_url = fields.Char()
    support_email = fields.Char()
    support_phone = fields.Char()
    api_key_ids = fields.One2many('mobile.api.key', 'app_config_id')
    banner_ids = fields.One2many('mobile.banner', 'app_config_id')
    slider_ids = fields.One2many('mobile.slider', 'app_config_id')
    notification_ids = fields.One2many('mobile.notification', 'app_config_id')
    device_ids = fields.One2many('mobile.device', 'app_config_id')


    @api.depends('website_id', 'website_id.pricelist_id', 'website_id.pricelist_id.currency_id', 'company_id.currency_id')
    def _compute_currency_id(self):
        for record in self:
            pricelist = getattr(record.website_id, 'pricelist_id', False)
            record.currency_id = (pricelist.currency_id if pricelist else False) or record.company_id.currency_id

    _sql_constraints = [
        ('website_company_unique', 'unique(website_id, company_id)', 'Only one mobile configuration is allowed per website and company.'),
    ]

    @api.constrains('primary_color', 'secondary_color', 'accent_color')
    def _check_hex_colors(self):
        for record in self:
            for color in (record.primary_color, record.secondary_color, record.accent_color):
                if color and (len(color) != 7 or not color.startswith('#')):
                    raise ValidationError(_('Colors must use #RRGGBB format.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('jwt_secret'):
                vals['jwt_secret'] = secrets.token_urlsafe(48)
        return super().create(vals_list)

    def action_open_api_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('API Logs'),
            'res_model': 'mobile.api.log',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('app_config_id', '=', self.id)],
            'context': {'default_app_config_id': self.id},
        }
