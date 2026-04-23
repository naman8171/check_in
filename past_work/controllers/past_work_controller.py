# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PastWorkController(http.Controller):

    @http.route('/past-work', type='http', auth='public', website=True)
    def past_work_index(self, filter=None, **kwargs):
        """
        Main portfolio listing page.
        Supports ?filter=<category_slug> for category filtering.
        """
        Project = request.env['past.work.project']
        Category = request.env['past.work.category']

        domain = [('state', '=', 'published')]
        active_category = None

        if filter and filter != '*':
            category = Category.sudo().search([('slug', '=', filter)], limit=1)
            if category:
                domain.append(('category_id', '=', category.id))
                active_category = category

        projects = Project.sudo().search(domain, order='sequence, name')
        categories = Category.sudo().search([
            ('id', 'in', Project.sudo().search(
                [('state', '=', 'published')]
            ).mapped('category_id').ids)
        ], order='sequence, name')

        return request.render('past_work.past_work_index_template', {
            'projects': projects,
            'categories': categories,
            'active_filter': filter or '*',
            'active_category': active_category,
        })

    @http.route('/past-work/<string:slug>', type='http', auth='public', website=True)
    def past_work_detail(self, slug, **kwargs):
        """
        Individual project detail page.
        """
        project = request.env['past.work.project'].sudo().search(
            [('slug', '=', slug), ('state', '=', 'published')],
            limit=1
        )
        if not project:
            return request.not_found()

        related_projects = request.env['past.work.project'].sudo().search(
            [
                ('category_id', '=', project.category_id.id),
                ('state', '=', 'published'),
                ('id', '!=', project.id),
            ],
            limit=3,
            order='sequence, name'
        )

        return request.render('past_work.past_work_detail_template', {
            'project': project,
            'related_projects': related_projects,
        })
