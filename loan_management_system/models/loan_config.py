from odoo import models, fields

class LoanConfig(models.Model):
    _name = "loan.config"
    _description = "Loan Configuration"

    name = fields.Char(string="Config Name", required=True)

    interest_rate = fields.Float(string="Interest Rate (%)")
    processing_fee = fields.Float(string="Processing Fee (%)")
    penalty_rate = fields.Float(string="Penalty Rate (%)")

    active = fields.Boolean(default=True)