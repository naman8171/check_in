from odoo import models, fields

class FinalFormulation(models.Model):
    _name = 'final.formulation'
    _description = 'Final Formulation'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier",
        ondelete='cascade'
    )
    ingredient = fields.Char(string="Ingredients")
    product_specification = fields.Char(string="Product Specifications")
    age1 = fields.Float(string="Age (%)")
    calculated_size = fields.Float(string="Size")
    rate_per_kg = fields.Float(string="Rate/KG")
    total_value = fields.Float(string="Value")
    
class FinalFormulation(models.Model):
    _name = 'supplier.details'
    _description = 'Final Formulation'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier",
        ondelete='cascade'
    )
    ingredient = fields.Char(string="Ingredients")
    product_specification = fields.Char(string="Product Specifications")
    supplier_detail = fields.Char(string="Supplier Details")
    contact_no = fields.Char(string="Contact Number")
    photo = fields.Binary(string="Upload Photo")
    
