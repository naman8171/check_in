from odoo import models, fields,api,_
import time

class TechnicalDossier(models.Model):
    _name = 'technical.dossier'
    _description = 'Technical Dossier'

    final_sensory_profile_title = fields.Char(string="Final Sensory Profile Title")

    taste = fields.Integer(string="Taste (Marking out of 5)")
    aroma = fields.Integer(string="Aroma (Marking out of 5)")
    mouthfeel = fields.Integer(string="Mouthfeel (Marking out of 5)")
    visual = fields.Integer(string="Visual (Marking out of 5)")
    aftertaste = fields.Integer(string="Aftertaste (Marking out of 5)")
    batch_no = fields.Char(string="Batch Number")


    name = fields.Char(
        string='Dossier Reference',
        required=True,
        readonly=True,
        copy=False,
        default='New'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'technical.dossier.sequence'
            ) or 'New'
        return super().create(vals) 


    delivery_picking_id = fields.Many2one(
        'delivery.picking',
        string="Delivery Picking",
        required=True
    )
    project_overview_title = fields.Char(
        string="Title"
    )

    product_concept_title = fields.Char(
        string="Title"
    )

    final_sensory_profile_title = fields.Char(
        string="Title"
    )

    final_formulation_title = fields.Char(
        string="Title"
    )

    ingredient_justification_title = fields.Char(
        string="Title"
    )

    manufacturing_process_flow_title = fields.Char(
        string="Title"
    )


    process_stages_title = fields.Char(
    string="Title"
    )

    quality_specification_title = fields.Char(
        string="Title"
    )

    packaging_compatibility_title = fields.Char(
        string="Title"
    )

    transport_storage_title = fields.Char(
        string="Title"
    )

    scale_up_title = fields.Char(
        string="Title"
    )

    cogs_analysis_title = fields.Char(
        string="Title"
    )

    project_id = fields.Many2one(
        'delivery.picking',
        string="Project ID",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product Name",
    )

    product_code = fields.Char(
        string="Product Code",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client Name",
    )

    category_id = fields.Many2one(
        "product.category",
        string="Category",
    )

    sensory_approval_date = fields.Date(
        string="Sensory Approval Date"
    )

    target_claims = fields.Text(string="Target Claims")
    market_positioning = fields.Text(string="Market Positioning")

    clean_label = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Clean Label")

    @api.onchange('delivery_picking_id')
    def onchange_picking_id(self):
        if self.delivery_picking_id:
            self.partner_id = self.delivery_picking_id.id
            self.product_id = self.delivery_picking_id.product_id.id
            if self.delivery_picking_id.product_id.default_code:
                self.product_code = self.delivery_picking_id.product_id.default_code
            self.category_id = self.product_id.categ_id.id
            self.sensory_approval_date = self.delivery_picking_id.start_date


    project_overview_ids = fields.One2many('project.overview', 'dossier_id')
    product_concept_ids = fields.One2many('product.concept', 'dossier_id')
    final_sensory_profile_ids = fields.One2many('final.sensory.profile', 'dossier_id')
    final_formulation_ids = fields.One2many('final.formulation', 'dossier_id')
    ingredient_justification_ids = fields.One2many('ingredient.justification', 'dossier_id')
    supplier_detail_ids = fields.One2many('supplier.details', 'dossier_id')
    manufacturing_process_flow_ids = fields.One2many('manufacturing.process.flow', 'dossier_id')
    process_stages_ids = fields.One2many('process.stages', 'dossier_id')
    quality_specification_ids = fields.One2many('quality.specification', 'dossier_id')
    packaging_compatibility_ids = fields.One2many('packaging.compatibility', 'dossier_id')
    transport_storage_ids = fields.One2many('transport.storage', 'dossier_id')
    scale_up_ids = fields.One2many('scale.up', 'dossier_id')
    cogs_analysis_ids = fields.One2many('cogs.analysis', 'dossier_id')


    final_formulation_ids = fields.One2many(
        'final.formulation',
        'dossier_id',
        string="Final Formulations"
    )

    def open_import_wizard(self):
        return {
            'name': 'Upload File',
            'type': 'ir.actions.act_window',
            'res_model': 'import.line.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_download_dump(self):
        return {
            'name': 'Download Dump File"',
            'type': 'ir.actions.act_window',
            'res_model': 'import.line.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
            'active_id': self.id,
            'import_type': self.env.context.get('import_type')
            }
        }

    def action_download_dump(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/inom_technical_dossier/static/files/technical_dossier_dump.xlsx?v={int(time.time())}',
            'target': 'self',
        }

    def open_import_file(self):
        return {
            'name': 'Upload File',
            'type': 'ir.actions.act_window',
            'res_model': 'import.line.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import_dump(self):
        return {
            'name': 'Download Dump File"',
            'type': 'ir.actions.act_window',
            'res_model': 'import.line.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
            'active_id': self.id,
            'import_type': self.env.context.get('import_type')
            }
        }

    def action_import_dump(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/inom_technical_dossier/static/files/technical_dossier_dump2.xlsx?v={int(time.time())}',
            'target': 'self',
        }

