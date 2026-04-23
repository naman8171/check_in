from odoo import http
from odoo.http import request


class PastWorkController(http.Controller):
    @http.route(["/past-work"], type="http", auth="public", website=True, sitemap=True)
    def past_work_listing(self, category=None, search=None, **kwargs):
        domain = [("active", "=", True)]
        if category:
            try:
                category_id = int(category)
            except ValueError:
                category_id = False
            if category_id:
                domain.append(("category_id", "=", category_id))
        if search:
            domain.extend([
                "|",
                "|",
                ("name", "ilike", search),
                ("description", "ilike", search),
                ("client_name", "ilike", search),
            ])

        works = request.env["past.work"].sudo().search(domain)
        categories = request.env["past.work.category"].sudo().search([])

        values = {
            "works": works,
            "categories": categories,
            "selected_category": int(category) if category and str(category).isdigit() else False,
            "search": search or "",
        }
        return request.render("past_work.past_work_page", values)

    @http.route(["/past-work/<int:work_id>"], type="http", auth="public", website=True, sitemap=True)
    def past_work_detail(self, work_id, **kwargs):
        work = request.env["past.work"].sudo().browse(work_id)
        if not work.exists() or not work.active:
            return request.not_found()

        return request.render("past_work.past_work_detail_page", {"work": work})
