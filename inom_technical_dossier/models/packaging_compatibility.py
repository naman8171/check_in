from odoo import models, fields

class PackagingCompatibility(models.Model):
    _name = 'packaging.compatibility'
    _description = 'Packaging Compatibility'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    packaging_type = fields.Selection([('bottle','Bottle'),
        ('pouch','Pouch'),('can','Can')],string="Packaging Type")
    packaging_material = fields.Selection([('pet','PET'),
        ('glass','Glass'),('tin','Tin'),('laminate','Laminate')],string="Packaging Material")
    filling_temp = fields.Char(string="Filling Temp")

    nitrogen_flush = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Nitrogen Flush")

    storage_condition = fields.Char(string="Storage Condition")
    transport_condition = fields.Char(string="Transport Condition")
