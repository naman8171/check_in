# -*- coding: utf-8 -*-
from odoo import fields, models


class MobileDevice(models.Model):
    _name = 'mobile.device'
    _description = 'Mobile Device'
    _inherit = ['mail.thread']
    _order = 'last_seen_at desc, id desc'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', index=True)
    user_id = fields.Many2one('res.users', index=True)
    company_id = fields.Many2one(related='app_config_id.company_id', store=True, readonly=True)
    website_id = fields.Many2one(related='app_config_id.website_id', store=True, readonly=True)
    platform = fields.Selection([('android', 'Android'), ('ios', 'iOS')], required=True)
    device_uuid = fields.Char(required=True, index=True)
    fcm_token = fields.Char(string='Firebase Token', required=True)
    app_version = fields.Char()
    os_version = fields.Char()
    language = fields.Char()
    currency_id = fields.Many2one('res.currency')
    last_seen_at = fields.Datetime(default=fields.Datetime.now)
    notification_enabled = fields.Boolean(default=True)

    _sql_constraints = [
        ('device_uuid_config_unique', 'unique(app_config_id, device_uuid)', 'Device UUID must be unique per mobile app configuration.'),
    ]

    def touch(self):
        self.write({'last_seen_at': fields.Datetime.now()})
