from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    past_work_spreadsheet_url = fields.Char(
        string="Past Work Spreadsheet CSV URL",
        config_parameter="website_past_work_catalog.spreadsheet_url",
        help="Public CSV export URL for the past work data source.",
    )
