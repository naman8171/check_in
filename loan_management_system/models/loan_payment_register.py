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
        if self.amount > self.loan_id.outstanding_amount:
            raise UserError(_("Payment amount cannot exceed the current outstanding amount."))

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
            paid_breakdown = self.env["loan.payment"].read_group(
                domain=[("installment_id", "=", line.id)],
                fields=["principal_component:sum", "interest_component:sum", "fee_component:sum", "penalty_component:sum"],
                groupby=[],
            )[0]
            principal_outstanding = max(line.principal_amount - (paid_breakdown.get("principal_component_sum") or 0.0), 0.0)
            interest_outstanding = max(line.interest_amount - (paid_breakdown.get("interest_component_sum") or 0.0), 0.0)
            fee_outstanding = max(line.fee_amount - (paid_breakdown.get("fee_component_sum") or 0.0), 0.0)
            penalty_outstanding = max(line.penalty_amount - (paid_breakdown.get("penalty_component_sum") or 0.0), 0.0)

            residual = pay
            penalty_component = min(penalty_outstanding, residual)
            residual -= penalty_component
            fee_component = min(fee_outstanding, residual)
            residual -= fee_component
            interest_component = min(interest_outstanding, residual)
            residual -= interest_component
            principal_component = min(principal_outstanding, residual)

            self.env["loan.payment"].create(
                {
                    "loan_id": self.loan_id.id,
                    "installment_id": line.id,
                    "payment_date": self.payment_date,
                    "journal_id": self.journal_id.id,
                    "amount": pay,
                    "principal_component": principal_component,
                    "interest_component": interest_component,
                    "fee_component": fee_component,
                    "penalty_component": penalty_component,
                    "note": self.note,
                }
            )
            remaining -= pay

        return {"type": "ir.actions.act_window_close"}
