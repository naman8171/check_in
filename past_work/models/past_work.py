from odoo import api, fields, models
from odoo.tools import html2plaintext


class PastWorkCategory(models.Model):
    _name = "past.work.category"
    _description = "Past Work Category"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    work_ids = fields.One2many("past.work", "category_id", string="Works")

    _sql_constraints = [
        ("past_work_category_name_uniq", "unique(name)", "Category name must be unique."),
    ]


class PastWorkTag(models.Model):
    _name = "past.work.tag"
    _description = "Past Work Tag"
    _order = "name"

    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ("past_work_tag_name_uniq", "unique(name)", "Tag name must be unique."),
    ]


class PastWork(models.Model):
    _name = "past.work"
    _description = "Past Work"
    _order = "sequence, completion_date desc, id desc"

    name = fields.Char(required=True, translate=True)
    description = fields.Html(sanitize=True, translate=True)
    description_short = fields.Char(compute="_compute_description_short", string="Short Description")
    image = fields.Image(max_width=2048, max_height=2048)
    category_id = fields.Many2one("past.work.category", required=True, ondelete="restrict")
    tag_ids = fields.Many2many("past.work.tag", string="Tags")
    client_name = fields.Char()
    completion_date = fields.Date()
    project_url = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    @api.depends("description")
    def _compute_description_short(self):
        for record in self:
            plain = html2plaintext(record.description or "").strip()
            record.description_short = (plain[:157] + "...") if len(plain) > 160 else plain
