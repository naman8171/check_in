# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InomNotificationTemplate(models.Model):
    """Registry of every branded/custom email template shipped by this module.

    New templates just need a new record here (usually via data XML) with a
    unique `technical_key`. That key is what the Python override code checks
    against the settings selection, so no other code needs to change when a
    new template is added later.
    """

    _name = "inom.notification.template"
    _description = "Inom Custom Notification Template"
    _order = "name"

    name = fields.Char(required=True)
    technical_key = fields.Char(
        required=True,
        help="Internal code referenced from Python (e.g. 'password_reset'). "
        "Must stay stable once used in code.",
    )
    view_id = fields.Many2one(
        "ir.ui.view",
        string="Overridden Email View",
        help="The core/base ir.ui.view (qweb) this template replaces.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "technical_key_uniq",
            "unique(technical_key)",
            "Technical key must be unique per notification template.",
        ),
    ]

    @api.model
    def is_template_enabled(self, technical_key):
        """Return True only if:
        1. The master 'use custom templates' toggle is ON, and
        2. This specific technical_key is one of the templates selected
           in Settings.
        """
        params = self.env["ir.config_parameter"].sudo()
        enabled = params.get_param(
            "inom_password_reset_email.enable_custom_email_templates"
        )
        if enabled not in ("True", "1", True):
            return False

        active_ids_param = params.get_param(
            "inom_password_reset_email.active_template_ids", ""
        )
        active_ids = [int(i) for i in active_ids_param.split(",") if i.strip()]
        if not active_ids:
            return False

        return bool(
            self.sudo().search(
                [("technical_key", "=", technical_key), ("id", "in", active_ids)],
                limit=1,
            )
        )
