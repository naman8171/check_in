from odoo import fields, models


class LoanInstallment(models.Model):
    _name = "loan.installment"
    _description = "Loan Installment"
    _order = "loan_id, sequence"

    loan_id = fields.Many2one("loan.loan", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="loan_id.company_id", store=True)
    currency_id = fields.Many2one(related="loan_id.currency_id", store=True)

    sequence = fields.Integer(required=True)
    due_date = fields.Date(required=True)
    principal_amount = fields.Monetary(required=True)
    interest_amount = fields.Monetary(required=True)
    amount = fields.Monetary(required=True)
    balance_amount = fields.Monetary(required=True)

    state = fields.Selection([("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid", tracking=True)
    paid_on = fields.Date()

    def action_mark_paid(self):
        self.write({"state": "paid", "paid_on": fields.Date.context_today(self)})

    def action_mark_unpaid(self):
        self.write({"state": "unpaid", "paid_on": False})
