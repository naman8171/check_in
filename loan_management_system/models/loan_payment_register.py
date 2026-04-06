from odoo import _, fields, models
from odoo.exceptions import UserError


class LoanPaymentRegister(models.TransientModel):
    _name = "loan.payment.register"
    _description = "Register Loan Payment"

    loan_id = fields.Many2one("loan.loan", required=True)
    installment_id = fields.Many2one("loan.installment", domain="[('loan_id', '=', loan_id), ('state', '!=', 'paid')]")
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(related="loan_id.currency_id")
    journal_id = fields.Many2one("account.journal", required=True, domain="[('type', 'in', ('bank', 'cash'))]")
    note = fields.Text()

    def action_confirm(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_("Payment amount must be greater than zero."))

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

        if remaining > 0 and not self.installment_id:
            for line in self.loan_id.installment_ids.filtered(lambda l: l.state != "paid"):
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
