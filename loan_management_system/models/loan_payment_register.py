from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LoanPaymentRegister(models.TransientModel):
    _name = "loan.payment.register"
    _description = "Register Loan Payment"

    loan_id = fields.Many2one("loan.loan", required=True)
    installment_id = fields.Many2one("loan.installment", domain="[('loan_id', '=', loan_id), ('state', '!=', 'paid')]")
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    payment_mode = fields.Selection([("regular", "Regular"), ("advance", "Advance")], default="regular", required=True)
    percent = fields.Float(string="Percent", default=100.0)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(related="loan_id.currency_id")
    journal_id = fields.Many2one("account.journal", required=True, domain="[('type', 'in', ('bank', 'cash'))]")
    note = fields.Text()

    @api.onchange("percent", "payment_mode", "loan_id")
    def _onchange_percent(self):
        for rec in self:
            if rec.payment_mode == "advance" and rec.loan_id:
                rec.amount = (rec.loan_id.outstanding_amount * rec.percent) / 100

    def action_confirm(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_("Payment amount must be greater than zero."))

        if self.payment_mode == "advance":
            target_lines = self.loan_id.installment_ids.filtered(lambda l: l.state != "paid")
        else:
            target_lines = self.installment_id or self.loan_id.installment_ids.filtered(lambda l: l.state != "paid")[:1]

        if not target_lines:
            raise UserError(_("No unpaid installment found for this loan."))

        remaining = self.amount
        for line in target_lines:
            if remaining <= 0:
                break
            payable = line.amount_due - line.amount_paid
            pay = min(payable, remaining)
            if pay <= 0:
                continue
            line.apply_payment(pay, self.payment_date)
            self.env["loan.payment"].create(
                {
                    "loan_id": self.loan_id.id,
                    "installment_id": line.id,
                    "payment_date": self.payment_date,
                    "journal_id": self.journal_id.id,
                    "amount": pay,
                    "principal_component": min(line.principal_amount, pay),
                    "interest_component": min(max(pay - line.principal_amount, 0.0), line.interest_amount),
                    "fee_component": line.fee_amount if pay >= (line.amount_due - line.fee_amount) else 0.0,
                    "penalty_component": line.penalty_amount,
                    "note": self.note,
                }
            )
            remaining -= pay

        return {"type": "ir.actions.act_window_close"}
