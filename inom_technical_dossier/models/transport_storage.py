from odoo import models, fields

class TransportStorage(models.Model):
    _name = 'transport.storage'
    _description = 'Transport & Storage'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    hot_fill = fields.Boolean(string="Hot Fill")
    cold_fill = fields.Boolean(string="Cold Fill")
    retort = fields.Boolean(string="Retort")
    aseptic = fields.Boolean(string="Aseptic")
