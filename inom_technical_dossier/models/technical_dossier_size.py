from odoo import models, fields


class TechnicalDossierSize(models.Model):
    _inherit = 'technical.dossier'
    
    size = fields.Integer(string="Size")
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


    def action_calculate_all_sizes(self):
        for rec in self:
            for line in rec.final_formulation_ids:
                line.calculated_size = (rec.size * line.age1) / 100
                line.total_value = (line.calculated_size*line.rate_per_kg)/1000
