{
    'name': 'Inom Stripe Fees on Invoice',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Show Stripe surcharge on customer invoices and track paid fee.',
    'license': 'LGPL-3',
    'depends': [
        'inom_stripe_fees',
        'account',
    ],
    'data': [
        'views/account_move_views.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
