from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    disable_automatic_emails = fields.Boolean(
        string="Disable Default Odoo Emails",
        config_parameter="disable_automatic_emails.enabled",
        help=(
            "Prevent Odoo from generating or sending default outgoing emails, "
            "including password reset emails, notifications, template emails, "
            "and queued outgoing emails."
        ),
    )
