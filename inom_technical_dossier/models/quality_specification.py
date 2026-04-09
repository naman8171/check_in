from odoo import models, fields

class QualitySpecification(models.Model):
    _name = 'quality.specification'
    _description = 'Quality Specification'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    parameter = fields.Char(string="Parameter")
    target = fields.Char(string="Target")
    minimum = fields.Char(string="Min")
    maximum = fields.Char(string="Max")
    test_method = fields.Char(string="Test Method")
    frequency = fields.Char(string="Frequency")
