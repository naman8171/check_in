{
    'name': 'Inom Stripe Transaction Fees',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Charge configurable extra fees on Stripe payments '
               '(domestic/international, with threshold).',
    'description': """
Inom Stripe Transaction Fees
============================
Adds configurable surcharges to Stripe payment transactions:

* Separate percentage + fixed fees for domestic and international customers
  (determined by comparing partner country with company country).
* Optional "waive fees above" threshold — if the base amount exceeds the limit,
  no fee is applied.
* Fee is added to the charged amount and stored on the transaction for
  reporting.

IMPORTANT: Passing card processing costs to customers ("surcharging") is
legally restricted in many jurisdictions (EU, UK, India, some US states) and
may violate Stripe's terms. Verify compliance before enabling.
""",
    'author': 'InomERP Pvt Ltd',
    'website': 'https://inomerp.in',
    'support': 'info@inomerp.in',
    'license': 'LGPL-3',
    'depends': [
        'payment_stripe',
        'account',
        'sale',
    ],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'views/account_payment_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'inom_stripe_fees/static/src/js/payment_form.js',
            'inom_stripe_fees/static/src/scss/payment_form.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
