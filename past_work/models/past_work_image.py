# -*- coding: utf-8 -*-
from odoo import models, fields


class PastWorkImage(models.Model):
    _name = 'past.work.image'
    _description = 'Past Work Project Gallery Image'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'past.work.project',
        string='Project',
        required=True,
        ondelete='cascade',
    )
    image = fields.Image(
        string='Image',
        required=True,
        max_width=1920,
        max_height=1080,
    )
    caption = fields.Char(string='Caption', translate=True)
    sequence = fields.Integer(string='Order', default=10)


class PastWorkTag(models.Model):
    _name = 'past.work.tag'
    _description = 'Past Work Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]
