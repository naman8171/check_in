# -*- coding: utf-8 -*-
{
    'name': 'Tree View Advanced Search',
    'version': '19.0.1.0.0',
    'summary': 'Per-column advanced filters in list and x2many tree views',
    'description': """
Adds a filter row directly in tree headers with single/multi value filters for
text, integer, float and relational columns.
    """,
    'category': 'Hidden',
    'author': 'Codex',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'tree_view_advanced_search/static/src/js/tree_view_advanced_search.js',
            'tree_view_advanced_search/static/src/scss/tree_view_advanced_search.scss',
        ],
    },
    'installable': True,
    'application': False,
}
