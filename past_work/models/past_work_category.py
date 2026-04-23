# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PastWorkCategory(models.Model):
    _name = 'past.work.category'
    _description = 'Past Work Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    slug = fields.Char(string='URL Slug', required=True,
                       help='Used for filtering in the frontend (e.g. filter-branding)')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    project_count = fields.Integer(
        string='Projects',
        compute='_compute_project_count',
        store=False
    )

    @api.depends('name')
    def _compute_project_count(self):
        for cat in self:
            cat.project_count = self.env['past.work.project'].search_count(
                [('category_id', '=', cat.id)]
            )

    _sql_constraints = [
        ('slug_unique', 'UNIQUE(slug)', 'The URL slug must be unique per category.'),
    ]
