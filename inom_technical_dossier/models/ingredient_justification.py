from odoo import models, fields

class IngredientJustification(models.Model):
    _name = 'ingredient.justification'
    _description = 'Ingredient Justification'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    why_used = fields.Text(string="Why Used?")
    functional_role = fields.Text(string="Functional Role")
    processing_behavior = fields.Text(string="Processing Behavior")
    ingredient = fields.Char(string="Ingredients")
    product_specification = fields.Char(string="Product Specifications")
