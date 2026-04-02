from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_late_checkin_alerts = fields.Boolean(
        string="Late Check-in Alerts",
        config_parameter="hr_attendance_late_checkin.enable_late_checkin_alerts",
        help="If enabled, late check-ins are marked and manager notification emails are sent.",
    )
