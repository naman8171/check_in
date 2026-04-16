{
    "name": "Stripe Payment Extra Fees",
    "summary": "Dedicated Stripe domestic/international extra fee configuration and display",
    "version": "19.0.1.0.0",
    "category": "Accounting/Payment Providers",
    "license": "LGPL-3",
    "author": "Custom",
    "depends": [
        "payment_stripe",
        "website_sale",
        "account_payment",
    ],
    "data": [
        "views/payment_provider_views.xml",
        "views/payment_transaction_views.xml",
    ],
    "installable": True,
    "application": False,
}
