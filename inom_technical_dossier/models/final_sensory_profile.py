from odoo import models, fields

class FinalSensoryProfile(models.Model):
    _name = 'final.sensory.profile'
    _description = 'Final Sensory Profile'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    taste = fields.Integer(string="Taste (Marking out of 5)")
    aroma = fields.Integer(string="Aroma (Marking out of 5)")
    mouthfeel = fields.Integer(string="Mouthfeel (Marking out of 5)")
    visual = fields.Integer(string="Visual (Marking out of 5)")
    aftertaste = fields.Integer(string="Aftertaste (Marking out of 5)")
