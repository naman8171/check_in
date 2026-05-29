# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MobileApiLog(models.Model):
    _name = 'mobile.api.log'
    _description = 'Mobile API Log'
    _order = 'create_date desc, id desc'
    _rec_name = 'endpoint'

    app_config_id = fields.Many2one('mobile.app.config', ondelete='set null', index=True)
    api_key_id = fields.Many2one('mobile.api.key', ondelete='set null', index=True)
    user_id = fields.Many2one('res.users', index=True)
    partner_id = fields.Many2one('res.partner', index=True)
    company_id = fields.Many2one('res.company', index=True)
    website_id = fields.Many2one('website', index=True)
    endpoint = fields.Char(required=True, index=True)
    method = fields.Char(required=True)
    ip_address = fields.Char()
    request_payload = fields.Text()
    response_payload = fields.Text()
    status_code = fields.Integer(default=200, index=True)
    duration_ms = fields.Integer()
    error_message = fields.Text()

    @api.autovacuum
    def _gc_mobile_api_logs(self):
        retention_days = int(self.env['ir.config_parameter'].sudo().get_param('mobile_commerce_api.log_retention_days', 30))
        deadline = fields.Datetime.subtract(fields.Datetime.now(), days=retention_days)
        self.sudo().search([('create_date', '<', deadline)]).unlink()
