# -*- coding: utf-8 -*-
{
    'name': 'Stripe Payment Extra Fees',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Add domestic and international extra fees to Stripe payment method',
    'description': """
        This module extends the Stripe payment provider in Odoo 19 Enterprise
        to support configurable extra fees:
        - Fixed and variable domestic fees
        - Fixed and variable international fees
        - Fee waiver based on order total amount
        - Automatic Stripe Fee product creation
    """,
    'author': 'Custom Development',
    'depends': [
        'payment_stripe',
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_stripe_extra_fees/static/src/js/stripe_fee_widget.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
