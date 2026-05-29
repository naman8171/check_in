# -*- coding: utf-8 -*-
from odoo import fields, models


class MobileWishlist(models.Model):
    _name = 'mobile.wishlist'
    _description = 'Mobile Customer Wishlist'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade', index=True)
    website_id = fields.Many2one('website', index=True)
    company_id = fields.Many2one('res.company', index=True)

    _sql_constraints = [
        ('partner_product_website_unique', 'unique(partner_id, product_tmpl_id, website_id)', 'Product is already in this customer wishlist.'),
    ]


class MobileProductComparison(models.Model):
    _name = 'mobile.product.comparison'
    _description = 'Mobile Product Comparison'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade', index=True)
    website_id = fields.Many2one('website', index=True)
    company_id = fields.Many2one('res.company', index=True)

    _sql_constraints = [
        ('partner_product_compare_unique', 'unique(partner_id, product_tmpl_id, website_id)', 'Product is already in comparison list.'),
    ]


class MobileProductReview(models.Model):
    _name = 'mobile.product.review'
    _description = 'Mobile Product Review'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', tracking=True)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    product_tmpl_id = fields.Many2one('product.template', required=True, ondelete='cascade', index=True)
    website_id = fields.Many2one('website', index=True)
    company_id = fields.Many2one('res.company', index=True)
    rating = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], required=True)
    comment = fields.Text(required=True)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})
