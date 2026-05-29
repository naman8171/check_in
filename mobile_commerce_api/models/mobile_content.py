# -*- coding: utf-8 -*-
from odoo import fields, models


class MobileBanner(models.Model):
    _name = 'mobile.banner'
    _description = 'Mobile Banner'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='app_config_id.company_id', store=True, readonly=True)
    website_id = fields.Many2one(related='app_config_id.website_id', store=True, readonly=True)
    banner_type = fields.Selection([
        ('home', 'Home Banner'),
        ('category', 'Category Banner'),
        ('promotion', 'Promotion'),
        ('splash', 'Splash Promotion'),
    ], default='home', required=True)
    image = fields.Image(required=True, max_width=2048, max_height=2048)
    mobile_image = fields.Image(max_width=1280, max_height=1280)
    title = fields.Char(translate=True)
    subtitle = fields.Char(translate=True)
    url = fields.Char()
    product_tmpl_id = fields.Many2one('product.template')
    category_id = fields.Many2one('product.public.category')
    date_start = fields.Datetime()
    date_end = fields.Datetime()


class MobileSlider(models.Model):
    _name = 'mobile.slider'
    _description = 'Mobile Home Slider'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    image = fields.Image(required=True, max_width=2048, max_height=2048)
    title = fields.Char(translate=True)
    subtitle = fields.Char(translate=True)
    cta_label = fields.Char(string='CTA Label', translate=True)
    cta_url = fields.Char(string='CTA URL')
    product_tmpl_id = fields.Many2one('product.template')
    category_id = fields.Many2one('product.public.category')


class MobileHomeSection(models.Model):
    _name = 'mobile.home.section'
    _description = 'Mobile Home Page Section'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    app_config_id = fields.Many2one('mobile.app.config', required=True, ondelete='cascade', index=True)
    section_type = fields.Selection([
        ('featured_products', 'Featured Products'),
        ('new_arrivals', 'New Arrivals'),
        ('best_sellers', 'Best Sellers'),
        ('hot_deals', 'Hot Deals'),
        ('featured_categories', 'Featured Categories'),
        ('custom_products', 'Custom Products'),
    ], required=True, default='featured_products')
    product_tmpl_ids = fields.Many2many('product.template', string='Products')
    category_ids = fields.Many2many('product.public.category', string='Categories')
    limit = fields.Integer(default=10)
