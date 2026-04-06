from datetime import timedelta

from odoo import api, fields, models


class LoanDashboard(models.TransientModel):
    _name = "loan.dashboard"
    _description = "Loan Dashboard"

    user_id = fields.Many2one("res.users", string="Users")
    borrower_id = fields.Many2one("res.partner", string="Borrower")
    loan_type_id = fields.Many2one("loan.type", string="Loan Type")
    date_range = fields.Selection(
        [
            ("lifetime", "Lifetime"),
            ("this_month", "This Month"),
            ("last_3_month", "Last 3 Months"),
            ("this_year", "This Year"),
        ],
        default="lifetime",
    )
    top_limit = fields.Integer(default=5)

    approved_amount = fields.Monetary(compute="_compute_metrics")
    disbursed_amount = fields.Monetary(compute="_compute_metrics")
    repayment_amount = fields.Monetary(compute="_compute_metrics")
    interest_amount = fields.Monetary(compute="_compute_metrics")
    lead_count = fields.Integer(compute="_compute_metrics")
    processing_fee_total = fields.Monetary(compute="_compute_metrics")
    closed_count = fields.Integer(compute="_compute_metrics")
    open_count = fields.Integer(compute="_compute_metrics")
    avg_interest_rate = fields.Float(compute="_compute_metrics")

    total_installment = fields.Integer(compute="_compute_installment_metrics")
    paid_installment = fields.Integer(compute="_compute_installment_metrics")
    unpaid_installment = fields.Integer(compute="_compute_installment_metrics")

    top_partner_ids = fields.Many2many("res.partner", compute="_compute_top_lists")
    top_installment_ids = fields.Many2many("loan.installment", compute="_compute_top_lists")

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id")

    def _loan_domain(self):
        self.ensure_one()
        domain = []
        if self.user_id:
            domain.append(("user_id", "=", self.user_id.id))
        if self.borrower_id:
            domain.append(("partner_id", "=", self.borrower_id.id))
        if self.loan_type_id:
            domain.append(("loan_type_id", "=", self.loan_type_id.id))

        today = fields.Date.today()
        if self.date_range == "this_month":
            domain.append(("application_date", ">=", today.replace(day=1)))
        elif self.date_range == "last_3_month":
            domain.append(("application_date", ">=", today - timedelta(days=90)))
        elif self.date_range == "this_year":
            domain.append(("application_date", ">=", today.replace(month=1, day=1)))
        return domain

    @api.depends("user_id", "borrower_id", "loan_type_id", "date_range")
    def _compute_metrics(self):
        lead_model = self.env["crm.lead"]
        for rec in self:
            domain = rec._loan_domain()
            loans = self.env["loan.loan"].search(domain)
            rec.approved_amount = sum(loans.filtered(lambda l: l.state in ("approved", "open", "closed")).mapped("principal_amount"))
            rec.disbursed_amount = sum(loans.mapped("disbursed_amount"))
            rec.repayment_amount = sum(loans.mapped("paid_amount"))
            rec.interest_amount = sum(loans.mapped("total_interest"))
            rec.processing_fee_total = sum(loans.mapped("processing_fee"))
            rec.closed_count = len(loans.filtered(lambda l: l.state == "closed"))
            rec.open_count = len(loans.filtered(lambda l: l.state == "open"))
            rec.avg_interest_rate = (sum(loans.mapped("interest_rate")) / len(loans)) if loans else 0.0
            rec.lead_count = lead_model.search_count([])

    @api.depends("user_id", "borrower_id", "loan_type_id", "date_range")
    def _compute_installment_metrics(self):
        for rec in self:
            loan_domain = rec._loan_domain()
            loans = self.env["loan.loan"].search(loan_domain)
            installments = self.env["loan.installment"].search([("loan_id", "in", loans.ids)])
            rec.total_installment = len(installments)
            rec.paid_installment = len(installments.filtered(lambda i: i.state == "paid"))
            rec.unpaid_installment = len(installments.filtered(lambda i: i.state != "paid"))

    @api.depends("user_id", "borrower_id", "loan_type_id", "date_range", "top_limit")
    def _compute_top_lists(self):
        for rec in self:
            loans = self.env["loan.loan"].search(rec._loan_domain())
            partner_group = self.env["loan.loan"].read_group(
                [("id", "in", loans.ids)],
                ["partner_id", "principal_amount:sum"],
                ["partner_id"],
                limit=max(rec.top_limit, 1),
                orderby="principal_amount desc",
            )
            partner_ids = [p["partner_id"][0] for p in partner_group if p.get("partner_id")]
            rec.top_partner_ids = [(6, 0, partner_ids)]

            installment_ids = self.env["loan.installment"].search(
                [("loan_id", "in", loans.ids)],
                limit=max(rec.top_limit, 1),
                order="amount_due desc",
            )
            rec.top_installment_ids = [(6, 0, installment_ids.ids)]

    def action_refresh(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "loan.dashboard",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
        }

    def action_print_dashboard(self):
        self.ensure_one()
        return self.env.ref("loan_management_system.action_report_loan_dashboard").report_action(self)
