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

    application_date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    first_due_date = fields.Date(required=True, tracking=True)
    loan_type = fields.Selection(
        [("personal", "Personal"), ("business", "Business"), ("mortgage", "Mortgage"), ("other", "Other")],
        default="personal",
        required=True,
        tracking=True,
    )

    principal_amount = fields.Monetary(required=True, tracking=True)
    interest_rate = fields.Float(help="Annual interest rate in percentage", tracking=True)
    term_months = fields.Integer(required=True, default=12, tracking=True)
    processing_fee = fields.Monetary(default=0.0)

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
    installment_count = fields.Integer(compute="_compute_installment_count")

    total_interest = fields.Monetary(compute="_compute_totals", store=True)
    total_amount = fields.Monetary(compute="_compute_totals", store=True)
    outstanding_amount = fields.Monetary(compute="_compute_totals", store=True)
    paid_amount = fields.Monetary(compute="_compute_totals", store=True)

    notes = fields.Text()

    @api.depends("installment_ids")
    def _compute_installment_count(self):
        for rec in self:
            rec.installment_count = len(rec.installment_ids)

    @api.depends("principal_amount", "installment_ids.interest_amount", "installment_ids.amount", "installment_ids.state")
    def _compute_totals(self):
        for rec in self:
            total_interest = sum(rec.installment_ids.mapped("interest_amount"))
            total_amount = rec.principal_amount + total_interest + rec.processing_fee
            paid_amount = sum(rec.installment_ids.filtered(lambda i: i.state == "paid").mapped("amount"))
            rec.total_interest = total_interest
            rec.total_amount = total_amount
            rec.paid_amount = paid_amount
            rec.outstanding_amount = total_amount - paid_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("loan.loan") or "New"
        return super().create(vals_list)

    def _check_before_schedule_generation(self):
        for rec in self:
            if rec.term_months <= 0:
                raise UserError(_("Term (months) must be greater than zero."))
            if rec.principal_amount <= 0:
                raise UserError(_("Principal amount must be greater than zero."))
            if not rec.first_due_date:
                raise UserError(_("Please set the first due date."))

    def action_generate_schedule(self):
        self._check_before_schedule_generation()
        for rec in self:
            rec.installment_ids.unlink()
            monthly_rate = (rec.interest_rate / 100.0) / 12.0
            principal_portion = rec.principal_amount / rec.term_months
            balance = rec.principal_amount
            due_date = rec.first_due_date

            for number in range(1, rec.term_months + 1):
                interest_amount = balance * monthly_rate
                amount = principal_portion + interest_amount
                ending_balance = balance - principal_portion
                self.env["loan.installment"].create(
                    {
                        "loan_id": rec.id,
                        "sequence": number,
                        "due_date": due_date,
                        "principal_amount": principal_portion,
                        "interest_amount": interest_amount,
                        "amount": amount,
                        "balance_amount": max(ending_balance, 0.0),
                    }
                )
                balance = ending_balance
                due_date = due_date + relativedelta(months=1)

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_disburse(self):
        self.write({"state": "disbursed"})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_close(self):
        for rec in self:
            if any(line.state != "paid" for line in rec.installment_ids):
                raise UserError(_("You can only close loans after all installments are paid."))
        self.write({"state": "closed"})

    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def action_view_installments(self):
        self.ensure_one()
        return {
            "name": _("Installments"),
            "type": "ir.actions.act_window",
            "res_model": "loan.installment",
            "view_mode": "tree,form",
            "domain": [("loan_id", "=", self.id)],
            "context": {"default_loan_id": self.id},
        }
