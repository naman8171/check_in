from odoo import models, fields

class ScaleUp(models.Model):
    _name = 'scale.up'
    _description = 'Scale-Up & Commercial Guidance'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )
    name = fields.Char(string="Name")
    sr_no = fields.Char(string="Serial Number")
    pilot_batch_size = fields.Char(string="Pilot Batch Size")
    commercial_batch_size = fields.Char(string="Commercial Batch Size")
    expected_yield = fields.Float(string="Expected Yield %")
    scale_up_risk_notes = fields.Text(string="Scale-up Risk Notes")
    machinery_required = fields.Text(string="Machinery Required")
    loss_assumption = fields.Float(string="Loss % Assumption")
