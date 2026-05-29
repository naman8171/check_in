# -*- coding: utf-8 -*-
{
    'name': 'Mobile Commerce API Builder',
    'version': '19.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Enterprise mobile commerce REST API layer for Android and iOS apps.',
    'description': """
Mobile Commerce API Builder
===========================
Provides a scalable Odoo 19 Enterprise mobile commerce backend inspired by
mobile app builder platforms. The module exposes secure, versioned REST APIs
for native Android and iOS applications, manages mobile app configuration,
Firebase push devices, API keys, banners, home-page merchandising, wishlist,
product comparison, product reviews, cart synchronization, checkout, order
tracking, API logging, and administration dashboards.

Key capabilities include JWT/token authentication, API key management, FCM
configuration, multi-company, multi-website, multi-currency, and multi-language
ready data models.
""",
    'author': 'InomERP Pvt Ltd',
    'website': 'https://inomerp.in',
    'support': 'info@inomerp.in',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'website',
        'website_sale',
        'sale_management',
        'stock',
        'account',
        'payment',
        'delivery',
        'mail',
        'portal',
    ],
    'data': [
        'security/mobile_commerce_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/ir_cron.xml',
        'views/mobile_app_config_views.xml',
        'views/mobile_banner_views.xml',
        'views/mobile_notification_views.xml',
        'views/mobile_device_views.xml',
        'views/mobile_api_key_views.xml',
        'views/mobile_api_log_views.xml',
        'views/mobile_catalog_views.xml',
        'views/mobile_dashboard_views.xml',
        'views/menus.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
}
