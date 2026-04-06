from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    explanation_activity_ids = fields.One2many(
        "module.explanation.activity", "employee_id", string="Module Explanation Activities"
    )
    explained_module_count = fields.Integer(
        string="Explained Modules",
        compute="_compute_explanation_metrics",
    )
    avg_explanation_rating = fields.Float(
        string="Average Rating",
        compute="_compute_explanation_metrics",
        digits=(16, 2),
    )
    total_explanation_hours = fields.Float(
        string="Total Explanation Hours",
        compute="_compute_explanation_metrics",
        digits=(16, 2),
    )
    performance_score = fields.Float(
        string="Performance Score",
        compute="_compute_explanation_metrics",
        help="Weighted score using average rating and count of completed explanations.",
        digits=(16, 2),
    )

    def _compute_explanation_metrics(self):
        activities_by_emp = {}
        if self.ids:
            groups = self.env["module.explanation.activity"].read_group(
                domain=[("employee_id", "in", self.ids), ("state", "=", "done")],
                fields=["employee_id", "actual_duration_hours:sum", "rating_value:avg"],
                groupby=["employee_id"],
                lazy=False,
            )
            activities_by_emp = {
                g["employee_id"][0]: {
                    "count": g["employee_id_count"],
                    "hours": g.get("actual_duration_hours_sum", 0.0),
                    "avg_rating": g.get("rating_value_avg", 0.0),
                }
                for g in groups
            }

        for employee in self:
            data = activities_by_emp.get(
                employee.id, {"count": 0, "hours": 0.0, "avg_rating": 0.0}
            )
            employee.explained_module_count = data["count"]
            employee.total_explanation_hours = data["hours"]
            employee.avg_explanation_rating = data["avg_rating"]
            employee.performance_score = data["avg_rating"] * (1 + (data["count"] / 10.0))
