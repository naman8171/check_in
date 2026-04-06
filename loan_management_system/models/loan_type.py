from odoo import fields, models


class LoanType(models.Model):
    _name = "loan.type"
    _description = "Loan Type"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
    min_amount = fields.Monetary()
    max_amount = fields.Monetary()
    default_interest_rate = fields.Float(help="Annual interest rate in percentage")
    default_term_months = fields.Integer(default=12)
    processing_fee_percent = fields.Float(help="Applied on principal amount")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True)

    journal_id = fields.Many2one("account.journal", domain="[('type', 'in', ('bank', 'cash'))]")
    income_account_id = fields.Many2one("account.account")
    receivable_account_id = fields.Many2one("account.account")
