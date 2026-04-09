from odoo import models, fields, api


class ProjectOverview(models.Model):
    _name = 'project.overview'
    _description = 'Project Overview'

    # 🔹 Link with Technical Dossier
    dossier_id = fields.Many2one(
        'technical.dossier',
        string="Technical Dossier",
        required=True,
        ondelete='cascade'
    )

    

    # ==========================================================
    # 🔥 COMPUTE METHOD
    # ==========================================================

    @api.depends(
        'dossier_id',
    )
    def _compute_project_details(self):
        for rec in self:
            picking = rec.dossier_id.delivery_picking_id
            if picking:
                rec.project_id = picking.id
