from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ModuleExplanationActivity(models.Model):
    _name = "module.explanation.activity"
    _description = "Module Explanation Activity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "assigned_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
    )
    module_name = fields.Char(string="Module Name", required=True, tracking=True)
    module_description = fields.Text(string="Description")

    employee_id = fields.Many2one(
        "hr.employee",
        string="Assigned Employee",
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        related="employee_id.user_id",
        string="User",
        store=True,
        index=True,
    )
    manager_id = fields.Many2one(
        "hr.employee",
        string="Assigned By",
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )

    assigned_date = fields.Date(
        string="Assigned Date",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    due_date = fields.Date(string="Due Date", tracking=True)
    explanation_date = fields.Date(string="Explanation Date", tracking=True)

    planned_duration_hours = fields.Float(
        string="Planned Duration (hours)",
        help="Estimated duration expected for explanation.",
    )
    actual_duration_hours = fields.Float(
        string="Actual Duration (hours)",
        help="Actual time spent for module explanation.",
        tracking=True,
    )
    effort_score = fields.Float(
        string="Effort Score",
        compute="_compute_effort_score",
        store=True,
        help="Effort compared to expected duration. 100 means exactly as planned.",
    )

    rating = fields.Selection(
        [
            ("1", "1 - Needs Improvement"),
            ("2", "2 - Fair"),
            ("3", "3 - Good"),
            ("4", "4 - Very Good"),
            ("5", "5 - Excellent"),
        ],
        string="Rating",
        tracking=True,
    )
    rating_value = fields.Float(
        string="Rating Value",
        compute="_compute_rating_value",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("done", "Evaluated"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        index=True,
    )

    employee_notes = fields.Text(string="Employee Notes")
    manager_feedback = fields.Text(string="Manager Feedback", tracking=True)

    @api.depends("planned_duration_hours", "actual_duration_hours")
    def _compute_effort_score(self):
        for rec in self:
            if rec.planned_duration_hours and rec.actual_duration_hours >= 0:
                rec.effort_score = (rec.actual_duration_hours / rec.planned_duration_hours) * 100
            else:
                rec.effort_score = 0.0

    @api.depends("rating")
    def _compute_rating_value(self):
        for rec in self:
            rec.rating_value = float(rec.rating) if rec.rating else 0.0

    @api.constrains("actual_duration_hours", "planned_duration_hours")
    def _check_duration(self):
        for rec in self:
            if rec.planned_duration_hours < 0 or rec.actual_duration_hours < 0:
                raise ValidationError("Durations cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "module.explanation.activity"
                ) or "New"
        return super().create(vals_list)

    def action_assign(self):
        self.write({"state": "assigned"})

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_submit(self):
        for rec in self:
            values = {"state": "submitted"}
            if not rec.explanation_date:
                values["explanation_date"] = fields.Date.context_today(self)
            rec.write(values)

    def action_mark_done(self):
        self.write({"state": "done"})

    def action_reset_draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "cancel"})
