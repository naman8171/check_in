# -*- coding: utf-8 -*-
{
    'name': 'Past Work Portfolio',
    'version': '19.0.1.0.0',
    'category': 'Portfolio',
    'summary': 'Manage and showcase past work projects with a minimal portfolio design',
    'description': """
        Past Work Portfolio Module for Odoo 19
        ======================================
        - Manage portfolio projects with categories, client info, timelines
        - Beautiful kanban/list views in the backend
        - Filter by category: Branding, Web Design, Print Design, Motion
        - Attach multiple images per project
        - Public-facing website page with MinimalFolio design
        - Full CRUD operations from the backend
    """,
    'author': 'Custom Development',
    'depends': ['base', 'mail', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/past_work_category_data.xml',
        'views/past_work_views.xml',
        'views/past_work_menu.xml',
        'views/past_work_website_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'past_work/static/src/css/past_work_backend.css',
        ],
        'website.assets_frontend': [
            'past_work/static/src/css/past_work_frontend.css',
            'past_work/static/src/js/past_work_frontend.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
