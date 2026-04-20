from odoo import api, fields, models
from odoo.exceptions import UserError


class CloneRecord(models.Model):
    _name = "clone.record"
    _description = "Cloned Workflow Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True, tracking=True)
    active = fields.Boolean(default=True)
    subject = fields.Char(required=True, tracking=True)
    customer_name = fields.Char(required=True, tracking=True)
    customer_email = fields.Char(required=True, tracking=True)
    customer_phone = fields.Char(tracking=True)
    company = fields.Char()
    category = fields.Selection(
        [
            ("general", "General"),
            ("billing", "Billing"),
            ("technical", "Technical"),
            ("other", "Other"),
        ],
        default="general",
        required=True,
        tracking=True,
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Urgent")],
        default="1",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("waiting", "Waiting"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    assigned_user_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
    description = fields.Html()
    internal_note = fields.Text()
    due_date = fields.Date(tracking=True)
    close_date = fields.Datetime(readonly=True)

    line_ids = fields.One2many("clone.record.line", "record_id", string="Checklist")
    line_count = fields.Integer(compute="_compute_line_count")

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("clone.record") or "New"
        return super().create(vals_list)

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_wait(self):
        self.write({"state": "waiting"})

    def action_done(self):
        self.write({"state": "done", "close_date": fields.Datetime.now()})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_draft(self):
        self.write({"state": "draft", "close_date": False})

    def action_send_summary_email(self):
        self.ensure_one()
        if not self.customer_email:
            raise UserError("Customer email is required to send summary email.")
        template = self.env.ref("exact_dashboard_clone.mail_template_clone_record_summary")
        template.send_mail(self.id, force_send=True)


class CloneRecordLine(models.Model):
    _name = "clone.record.line"
    _description = "Cloned Workflow Checklist Item"

    record_id = fields.Many2one("clone.record", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    is_done = fields.Boolean(default=False)
