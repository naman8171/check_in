from odoo import models, fields

class CogsAnalysis(models.Model):
    _name = 'cogs.analysis'
    _description = 'COGS Analysis'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    cost_component = fields.Char(string="Cost Component")
    amount = fields.Float(string="Amount")

    