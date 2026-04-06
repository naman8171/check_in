from datetime import date

from odoo import api, fields, models


class LoanInstallment(models.Model):
    _name = "loan.installment"
    _description = "Loan Installment"
    _order = "loan_id, sequence"

    loan_id = fields.Many2one("loan.loan", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="loan_id.company_id", store=True)
    currency_id = fields.Many2one(related="loan_id.currency_id", store=True)

    sequence = fields.Integer(required=True)
    due_date = fields.Date(required=True)
    opening_balance = fields.Monetary(required=True)
    principal_amount = fields.Monetary(required=True)
    interest_amount = fields.Monetary(required=True)
    fee_amount = fields.Monetary(default=0.0)
    penalty_amount = fields.Monetary(default=0.0)
    amount_due = fields.Monetary(required=True)
    amount_paid = fields.Monetary(default=0.0)
    balance_amount = fields.Monetary(required=True)

    state = fields.Selection(
        [("unpaid", "Unpaid"), ("partial", "Partially Paid"), ("paid", "Paid")],
        default="unpaid",
    )
    paid_on = fields.Date()
    late_days = fields.Integer(compute="_compute_late_days")

    @api.depends("due_date", "state")
    def _compute_late_days(self):
        today = date.today()
        for rec in self:
            if rec.state == "paid" or not rec.due_date:
                rec.late_days = 0
            else:
                rec.late_days = max((today - rec.due_date).days, 0)

    def apply_payment(self, amount, payment_date):
        for rec in self:
            new_paid = rec.amount_paid + amount
            vals = {"amount_paid": new_paid, "paid_on": payment_date}
            if new_paid >= rec.amount_due:
                vals["state"] = "paid"
            elif new_paid > 0:
                vals["state"] = "partial"
            rec.write(vals)

    def action_mark_paid(self):
        for rec in self:
            rec.write({"state": "paid", "amount_paid": rec.amount_due, "paid_on": fields.Date.context_today(self)})

    def action_mark_unpaid(self):
        self.write({"state": "unpaid", "amount_paid": 0.0, "paid_on": False})
