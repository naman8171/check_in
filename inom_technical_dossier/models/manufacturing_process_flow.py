from odoo import models, fields

class ManufacturingProcessFlow(models.Model):
    _name = 'manufacturing.process.flow'
    _description = 'Manufacturing Process Flow'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    step_no = fields.Integer(string="Step No")
    process_step = fields.Char(string="Process Step")
    temperature = fields.Char(string="Temp")
    time = fields.Char(string="Time")
    rpm = fields.Char(string="RPM")
    equipment = fields.Char(string="Equipment")
    remarks = fields.Text(string="Remarks")
