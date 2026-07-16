# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_custom_email_templates = fields.Boolean(
        string="Use Custom Branded Email Templates",
        config_parameter="inom_password_reset_email.enable_custom_email_templates",
        help="Master switch. When off, all notifications fall back to "
        "Odoo's default behavior and none of the templates below apply.",
    )
    active_notification_template_ids = fields.Many2many(
        "inom.notification.template",
        string="Active Templates",
        help="Only the templates selected here will actually send an "
        "email notification. Unselected templates will NOT be sent.",
    )

    # Many2many fields cannot be stored via config_parameter="..." directly
    # (that shortcut only works for simple field types), so we persist the
    # selected ids ourselves as a comma-separated string.
    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "inom_password_reset_email.active_template_ids",
            ",".join(str(i) for i in self.active_notification_template_ids.ids),
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("inom_password_reset_email.active_template_ids", "")
        )
        ids = [int(i) for i in param.split(",") if i.strip()]
        res["active_notification_template_ids"] = [(6, 0, ids)]
        return res
