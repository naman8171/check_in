from odoo import models, fields

class ProcessStages(models.Model):
    _name = 'process.stages'
    _description = 'Process Stages / Procedure / CCP'

    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier"
    )

    step_no = fields.Integer(string="Step No")
    process_stage = fields.Char(string="Process Stage")
    procedure = fields.Text(string="Procedure")
    key_parameters = fields.Text(string="Key Parameters")
    ccp_control_measure = fields.Text(string="CCP / Control Measure")
