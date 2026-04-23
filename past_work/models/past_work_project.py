# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class PastWorkProject(models.Model):
    _name = 'past.work.project'
    _description = 'Past Work Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # ─── Basic Info ───────────────────────────────────────────────
    name = fields.Char(
        string='Project Name', required=True, tracking=True, translate=True
    )
    subtitle = fields.Char(
        string='Subtitle / Tagline', translate=True,
        help='Short description shown on the portfolio card'
    )
    description = fields.Html(
        string='Project Overview', translate=True,
        help='Full description shown on the project detail page'
    )
    challenge = fields.Html(
        string='The Challenge', translate=True
    )
    approach = fields.Html(
        string='Our Approach', translate=True
    )

    # ─── Classification ───────────────────────────────────────────
    category_id = fields.Many2one(
        'past.work.category',
        string='Category',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    tag_ids = fields.Many2many(
        'past.work.tag',
        string='Tags',
    )

    # ─── Project Meta ─────────────────────────────────────────────
    client_name = fields.Char(string='Client Name', tracking=True)
    timeline = fields.Char(
        string='Timeline',
        help='e.g. "8 Months" or "Jan 2024 – Sep 2024"'
    )
    year = fields.Char(
        string='Year',
        help='Year of project completion (e.g. 2024)'
    )
    services = fields.Char(
        string='Services Provided',
        help='e.g. "UX/UI Design, Development"'
    )
    project_url = fields.Char(string='Live Project URL')

    # ─── Media ────────────────────────────────────────────────────
    cover_image = fields.Image(
        string='Cover Image',
        max_width=1920, max_height=1080,
        help='Main image shown on the portfolio grid card'
    )
    image_ids = fields.One2many(
        'past.work.image',
        'project_id',
        string='Gallery Images',
    )

    # ─── Publishing ───────────────────────────────────────────────
    state = fields.Selection(
        [('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')],
        string='Status',
        default='draft',
        tracking=True,
        required=True,
    )
    website_published = fields.Boolean(
        string='Published on Website',
        compute='_compute_website_published',
        inverse='_inverse_website_published',
        store=True,
    )
    sequence = fields.Integer(string='Display Order', default=10)
    featured = fields.Boolean(string='Featured', default=False)

    # ─── Slug for URL ─────────────────────────────────────────────
    slug = fields.Char(
        string='URL Slug',
        compute='_compute_slug',
        store=True,
        readonly=False,
    )

    # ─── Computed ─────────────────────────────────────────────────
    image_count = fields.Integer(
        string='Gallery Images',
        compute='_compute_image_count',
        store=False,
    )

    @api.depends('state')
    def _compute_website_published(self):
        for rec in self:
            rec.website_published = rec.state == 'published'

    def _inverse_website_published(self):
        for rec in self:
            rec.state = 'published' if rec.website_published else 'draft'

    @api.depends('name')
    def _compute_slug(self):
        for rec in self:
            if rec.name:
                slug = rec.name.lower().strip()
                for ch in [' ', '/', '\\', '&', '%', '#', '?', '+']:
                    slug = slug.replace(ch, '-')
                rec.slug = slug
            else:
                rec.slug = ''

    def _compute_image_count(self):
        for rec in self:
            rec.image_count = len(rec.image_ids)

    # ─── Actions ──────────────────────────────────────────────────
    def action_publish(self):
        self.write({'state': 'published'})

    def action_unpublish(self):
        self.write({'state': 'draft'})

    def action_archive_project(self):
        self.write({'state': 'archived'})

    def action_view_on_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/past-work/%s' % self.slug,
            'target': 'new',
        }
