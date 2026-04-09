from odoo import models, fields

class ProductConcept(models.Model):
    _name = 'product.concept'
    _description = 'Product Concept & Positioning'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    target_claims = fields.Text(string="Target Claims")
    market_positioning = fields.Text(string="Market Positioning")

    clean_label = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Clean Label")
