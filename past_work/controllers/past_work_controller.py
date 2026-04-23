# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PastWorkController(http.Controller):

    @http.route('/past-work', type='http', auth='public', website=True)
    def past_work_index(self, **kwargs):
        """
        Main portfolio listing page.
        Shows only published projects created in backend.
        """
        Project = request.env['past.work.project']
        projects = Project.sudo().search([('state', '=', 'published')], order='sequence, name')

        return request.render('past_work.past_work_index_template', {
            'projects': projects,
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
