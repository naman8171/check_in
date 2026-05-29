# -*- coding: utf-8 -*-
import hashlib
import secrets

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MobileApiKey(models.Model):
    _name = 'mobile.api.key'
    _description = 'Mobile API Key'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='app_config_id.company_id', store=True, readonly=True)
    website_id = fields.Many2one(related='app_config_id.website_id', store=True, readonly=True)
    platform = fields.Selection([('android', 'Android'), ('ios', 'iOS'), ('web', 'Web'), ('server', 'Server')], default='android', required=True)
    key_prefix = fields.Char(readonly=True, copy=False)
    key_hash = fields.Char(readonly=True, copy=False, groups='mobile_commerce_api.group_mobile_admin')
    generated_key = fields.Char(string='Generated Key (copy once)', readonly=True, copy=False, groups='mobile_commerce_api.group_mobile_admin')
    last_used_at = fields.Datetime(readonly=True)
    expires_at = fields.Datetime()
    allowed_origin = fields.Char(help='Optional comma-separated list of allowed bundle IDs, package names, or origins.')
    request_count = fields.Integer(readonly=True)
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records.filtered(lambda item: not item.key_hash):
            record.action_generate_key()
        return records

    def action_generate_key(self):
        for record in self:
            token = 'mca_%s' % secrets.token_urlsafe(32)
            record.write({
                'key_prefix': token[:12],
                'key_hash': hashlib.sha256(token.encode()).hexdigest(),
                'generated_key': token,
            })
        return True

    def action_clear_generated_key(self):
        self.write({'generated_key': False})

    @api.model
    def authenticate(self, api_key):
        if not api_key:
            return self.browse()
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_rec = self.sudo().search([('key_hash', '=', key_hash), ('active', '=', True)], limit=1)
        if api_key_rec and api_key_rec.expires_at and api_key_rec.expires_at < fields.Datetime.now():
            raise UserError(_('API key has expired.'))
        if api_key_rec:
            api_key_rec.sudo().write({
                'last_used_at': fields.Datetime.now(),
                'request_count': api_key_rec.request_count + 1,
            })
        return api_key_rec
