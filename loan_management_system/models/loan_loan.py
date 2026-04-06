from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LoanLoan(models.Model):
    _name = "loan.loan"
    _description = "Loan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(default="New", copy=False, readonly=True, tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True, readonly=True)
    user_id = fields.Many2one("res.users", string="Loan Officer", default=lambda self: self.env.user, tracking=True)

    loan_type_id = fields.Many2one("loan.type", required=True, tracking=True)
    loan_type = fields.Selection(related="loan_type_id.code", string="Loan Code", store=True)
    purpose = fields.Text()

    application_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    approval_date = fields.Date(tracking=True)
    disbursement_date = fields.Date(tracking=True)
    first_due_date = fields.Date(required=True, tracking=True)

    principal_amount = fields.Monetary(required=True, tracking=True)
    interest_rate = fields.Float(help="Annual interest rate in percentage", tracking=True)
    term_months = fields.Integer(required=True, default=12, tracking=True)
    grace_period_months = fields.Integer(default=0)
    processing_fee = fields.Monetary(default=0.0)
    penalty_rate = fields.Float(default=0.0, help="Monthly penalty rate for overdue installments")

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("disbursed", "Disbursed"),
            ("closed", "Closed"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        tracking=True,
        required=True,
    )

    installment_ids = fields.One2many("loan.installment", "loan_id", string="Installments", copy=False)
    payment_ids = fields.One2many("loan.payment", "loan_id", string="Payments", copy=False)

    installment_count = fields.Integer(compute="_compute_counts")
    payment_count = fields.Integer(compute="_compute_counts")

    total_interest = fields.Monetary(compute="_compute_totals", store=True)
    total_fees = fields.Monetary(compute="_compute_totals", store=True)
    total_amount = fields.Monetary(compute="_compute_totals", store=True)
    outstanding_amount = fields.Monetary(compute="_compute_totals", store=True)
    paid_amount = fields.Monetary(compute="_compute_totals", store=True)
    next_due_date = fields.Date(compute="_compute_next_due", store=True)
    next_due_amount = fields.Monetary(compute="_compute_next_due", store=True)

    notes = fields.Text()

    @api.onchange("loan_type_id")
    def _onchange_loan_type_id(self):
        for rec in self:
            if rec.loan_type_id:
                rec.interest_rate = rec.loan_type_id.default_interest_rate
                rec.term_months = rec.loan_type_id.default_term_months
                rec.processing_fee = (rec.principal_amount * rec.loan_type_id.processing_fee_percent) / 100 if rec.principal_amount else 0

    @api.depends("installment_ids", "payment_ids")
    def _compute_counts(self):
        for rec in self:
            rec.installment_count = len(rec.installment_ids)
            rec.payment_count = len(rec.payment_ids)

    @api.depends(
        "principal_amount",
        "processing_fee",
        "installment_ids.interest_amount",
        "installment_ids.fee_amount",
        "installment_ids.amount_due",
        "installment_ids.amount_paid",
    )
    def _compute_totals(self):
        for rec in self:
            total_interest = sum(rec.installment_ids.mapped("interest_amount"))
            total_fees = rec.processing_fee + sum(rec.installment_ids.mapped("fee_amount"))
            total_due = sum(rec.installment_ids.mapped("amount_due")) + rec.processing_fee
            paid_amount = sum(rec.installment_ids.mapped("amount_paid"))
            rec.total_interest = total_interest
            rec.total_fees = total_fees
            rec.total_amount = total_due if total_due else rec.principal_amount + total_interest + total_fees
            rec.paid_amount = paid_amount
            rec.outstanding_amount = rec.total_amount - paid_amount

    @api.depends("installment_ids.state", "installment_ids.due_date", "installment_ids.amount_due", "installment_ids.amount_paid")
    def _compute_next_due(self):
        for rec in self:
            upcoming = rec.installment_ids.filtered(lambda l: l.state != "paid").sorted(key=lambda l: l.due_date or fields.Date.today())
            if upcoming:
                rec.next_due_date = upcoming[0].due_date
                rec.next_due_amount = upcoming[0].amount_due - upcoming[0].amount_paid
            else:
                rec.next_due_date = False
                rec.next_due_amount = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("loan.loan") or "New"
            if vals.get("loan_type_id") and not vals.get("interest_rate"):
                loan_type = self.env["loan.type"].browse(vals["loan_type_id"])
                vals["interest_rate"] = loan_type.default_interest_rate
                vals["term_months"] = vals.get("term_months") or loan_type.default_term_months
        return super().create(vals_list)

    def _check_before_schedule_generation(self):
        for rec in self:
            if rec.term_months <= 0:
                raise UserError(_("Term (months) must be greater than zero."))
            if rec.principal_amount <= 0:
                raise UserError(_("Principal amount must be greater than zero."))
            if not rec.first_due_date:
                raise UserError(_("Please set the first due date."))
            if rec.loan_type_id.min_amount and rec.principal_amount < rec.loan_type_id.min_amount:
                raise UserError(_("Amount is below minimum allowed for this loan type."))
            if rec.loan_type_id.max_amount and rec.principal_amount > rec.loan_type_id.max_amount:
                raise UserError(_("Amount exceeds maximum allowed for this loan type."))

    def action_generate_schedule(self):
        self._check_before_schedule_generation()
        for rec in self:
            rec.installment_ids.unlink()
            rate = (rec.interest_rate / 100.0) / 12.0
            months = rec.term_months
            principal = rec.principal_amount

            if rate:
                emi = (principal * rate * (1 + rate) ** months) / (((1 + rate) ** months) - 1)
            else:
                emi = principal / months

            balance = principal
            due_date = rec.first_due_date + relativedelta(months=rec.grace_period_months)
            for number in range(1, months + 1):
                interest_amount = balance * rate
                principal_portion = emi - interest_amount
                if number == months:
                    principal_portion = balance
                    emi = principal_portion + interest_amount
                ending_balance = balance - principal_portion
                penalty = 0.0
                self.env["loan.installment"].create(
                    {
                        "loan_id": rec.id,
                        "sequence": number,
                        "due_date": due_date,
                        "opening_balance": balance,
                        "principal_amount": principal_portion,
                        "interest_amount": interest_amount,
                        "fee_amount": 0.0,
                        "penalty_amount": penalty,
                        "amount_due": emi + penalty,
                        "balance_amount": max(ending_balance, 0.0),
                    }
                )
                balance = ending_balance
                due_date = due_date + relativedelta(months=1)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved", "approval_date": fields.Date.context_today(self)})

    def action_disburse(self):
        self.write({"state": "disbursed", "disbursement_date": fields.Date.context_today(self)})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_close(self):
        for rec in self:
            if any(line.state != "paid" for line in rec.installment_ids):
                raise UserError(_("You can only close loans after all installments are paid."))
        self.write({"state": "closed"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_register_payment(self):
        self.ensure_one()
        return {
            "name": _("Register Payment"),
            "type": "ir.actions.act_window",
            "res_model": "loan.payment.register",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_loan_id": self.id,
                "default_amount": self.next_due_amount or self.outstanding_amount,
                "default_journal_id": self.loan_type_id.journal_id.id,
            },
        }

    def action_view_installments(self):
        self.ensure_one()
        return {
            "name": _("Installments"),
            "type": "ir.actions.act_window",
            "res_model": "loan.installment",
            "view_mode": "tree,form,pivot,graph",
            "domain": [("loan_id", "=", self.id)],
            "context": {"default_loan_id": self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            "name": _("Payments"),
            "type": "ir.actions.act_window",
            "res_model": "loan.payment",
            "view_mode": "tree,form,pivot,graph",
            "domain": [("loan_id", "=", self.id)],
            "context": {"default_loan_id": self.id},
        }
