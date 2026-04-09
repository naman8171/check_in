from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    first_pdf = fields.Binary("First PDF")
    second_pdf = fields.Binary("Second PDF")
    last_pdf = fields.Binary("Last PDF")

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()

        params.set_param(
            'inom_technical_dossier.first_pdf',
            self.first_pdf or False
        )

        params.set_param(
            'inom_technical_dossier.second_pdf',
            self.second_pdf or False
        )

        params.set_param(
            'inom_technical_dossier.last_pdf',
            self.last_pdf or False
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()

        res.update(
            first_pdf=params.get_param('inom_technical_dossier.first_pdf'),
            second_pdf=params.get_param('inom_technical_dossier.second_pdf'),
            last_pdf=params.get_param('inom_technical_dossier.last_pdf'),
        )
        return res






# from odoo import models, fields, api

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     first = fields.Binary(string="First File")
#     last = fields.Binary(string="Last File")

#     def set_values(self):
#         super().set_values()
#         self.env['ir.config_parameter'].sudo().set_param(
#             'technical_dossier.first', self.first or ''
#         )
#         self.env['ir.config_parameter'].sudo().set_param(
#             'technical_dossier.last', self.last or ''
#         )

#     @api.model
#     def get_values(self):
#         res = super().get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         res.update(
#             first=params.get_param('technical_dossier.first', default=''),
#             last=params.get_param('technical_dossier.last', default=''),
#         )
#         return res
