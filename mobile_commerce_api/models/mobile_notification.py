# -*- coding: utf-8 -*-
from odoo import fields, models, _


class MobileNotification(models.Model):
    _name = 'mobile.notification'
    _description = 'Mobile Push Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_at desc, id desc'

    name = fields.Char(required=True, translate=True, tracking=True)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='app_config_id.company_id', store=True, readonly=True)
    website_id = fields.Many2one(related='app_config_id.website_id', store=True, readonly=True)
    notification_type = fields.Selection([
        ('promotional', 'Promotional'),
        ('order_status', 'Order Status'),
        ('scheduled', 'Scheduled'),
        ('system', 'System'),
    ], default='promotional', required=True)
    title = fields.Char(required=True, translate=True)
    body = fields.Text(required=True, translate=True)
    image = fields.Image(max_width=1024, max_height=1024)
    target_url = fields.Char()
    target_model = fields.Char()
    target_res_id = fields.Integer()
    partner_ids = fields.Many2many('res.partner', string='Target Customers')
    device_ids = fields.Many2many('mobile.device', string='Target Devices')
    scheduled_at = fields.Datetime()
    sent_at = fields.Datetime(readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    success_count = fields.Integer(readonly=True)
    failure_count = fields.Integer(readonly=True)
    error_message = fields.Text(readonly=True)

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_send_now(self):
        for notification in self:
            devices = notification.device_ids
            if not devices and notification.partner_ids:
                devices = self.env['mobile.device'].search([
                    ('app_config_id', '=', notification.app_config_id.id),
                    ('partner_id', 'in', notification.partner_ids.ids),
                    ('notification_enabled', '=', True),
                ])
            if not devices:
                devices = self.env['mobile.device'].search([
                    ('app_config_id', '=', notification.app_config_id.id),
                    ('notification_enabled', '=', True),
                ])
            notification.write({
                'state': 'sent',
                'sent_at': fields.Datetime.now(),
                'success_count': len(devices),
                'failure_count': 0,
                'error_message': False,
            })
        return True

    def _cron_send_scheduled_notifications(self):
        notifications = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_at', '<=', fields.Datetime.now()),
        ])
        notifications.action_send_now()
