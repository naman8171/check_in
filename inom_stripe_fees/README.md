# Inom Stripe Transaction Fees — Odoo 19

A lightweight module that re-implements the old Odoo payment-fee feature,
scoped to Stripe. Equivalent functionality to popular paid alternatives, but
under LGPL-3 so you can modify and redistribute freely.

**Author:** InomERP Pvt Ltd
**Website:** https://inomerp.in
**Support:** info@inomerp.in

## What it does

- Adds a **Custom Fees** tab on the Stripe payment provider with:
  - Domestic / International **percentage** fees
  - Domestic / International **fixed** fees
  - A **"Waive above X"** threshold
- Determines domestic vs international by comparing partner country with
  company country.
- Adds the computed surcharge to the transaction amount **before** Stripe
  processes it, so Stripe captures base + fee.
- Records both `base_amount` and `extra_fees` on `payment.transaction` for
  reporting.

## Troubleshooting — "I can't see the fee in the payment modal"

The fee is applied in **two places**:

1. **Backend (guaranteed):** `payment.transaction.create()` override injects
   the fee into `amount` before Stripe is called. Verify this works:
   - Make a test payment in Stripe test mode.
   - Open **Invoicing → Configuration → Payment Transactions** and find
     your transaction.
   - You should see `Base Amount`, `Extra Fees`, and `Amount` (base + fee).
   - Check the Stripe Dashboard — the captured charge should equal
     `base + fee`.

2. **Frontend (visible breakdown):** the JS widget fetches
   `/inom_stripe_fees/config` and injects a Base / Fee / Total block
   below the Stripe payment option.

If the breakdown doesn't appear:

- **Hard-refresh the browser** (Ctrl+Shift+R) — stale asset bundle is the
  #1 cause.
- **Regenerate assets**: from the Odoo shell or developer tools, delete
  `ir.attachment` records matching `/web/assets/%` — they'll rebuild.
- **Check the browser console** for errors. The widget logs nothing on
  success; if you see JS errors, the selector may not match your theme.
- **Verify the endpoint**: open devtools → Network tab → pay an invoice →
  look for a POST to `/inom_stripe_fees/config`. The response should be:
  ```json
  {"active": true, "is_domestic": true, "pct": 2.0, "fixed": 0.30, ...}
  ```
  If `active: false`, your provider setup is wrong — check that
  `fees_custom_active` is True and rates are non-zero.
- **Confirm the radio input**: inspect the Stripe option in the modal and
  confirm it has `name="o_payment_radio"` and
  `data-provider-code="stripe"`. If the attribute name differs in your
  theme, update the selectors in `static/src/js/payment_form.js`.

## Install

1. Copy the `inom_stripe_fees/` folder into your Odoo addons path.
2. Restart Odoo and run: **Apps → Update Apps List → Install "Inom Stripe
   Transaction Fees"**.
3. Go to **Invoicing → Configuration → Payment Providers → Stripe** and open
   the new **Custom Fees** tab to configure rates.

## Important caveats

### Legal / compliance
Surcharging card payments is **regulated or banned** in many places:
- **EU & UK**: PSD2 / Consumer Rights Directive prohibits surcharges on
  consumer debit/credit cards.
- **India**: RBI restrictions on MDR pass-through for RuPay and debit cards.
- **US**: Some states (CT, MA, ME) restrict it; others cap it.
- **Stripe ToS**: Stripe's own rules may prohibit surcharging depending on
  region and card scheme — check before enabling.

Common compliant alternatives:
- Show it as a **"convenience fee"** that is the same across all payment
  methods.
- Apply only to **B2B** transactions where rules are looser.
- Advertise gross prices and offer a **cash discount** instead.

### Technical notes
- The `create()` override on `payment.transaction` injects the fee on
  transaction creation. This works for the standard `/payment/transaction`
  flow. If you use custom controllers, verify the fee is applied there too.
- The frontend JS badge (`static/src/js/payment_form.js`) is a **scaffold** —
  the DOM selectors may need tweaking because Odoo 19's payment form markup
  differs slightly between checkout, invoice portal, and /my/payment. You
  also need to expose the provider's fee config as `data-*` attributes on
  the payment radio input (QWeb template inheritance on
  `payment.form` — not included here to keep the module minimal).

## Test checklist

- [ ] Create a Stripe test transaction from website checkout → confirm Stripe
      dashboard shows **base + fee**, and `payment.transaction` shows both
      `base_amount` and `extra_fees`.
- [ ] Change delivery address to a different country → international rates
      apply.
- [ ] Raise amount above `fees_free_limit` → no fee applied.
- [ ] Pay an invoice from the customer portal → fee applied there too.
- [ ] Disable `fees_custom_active` → fee drops to zero.

## Files

```
inom_stripe_fees/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── payment_provider.py       # Fee config fields + _compute_custom_fees
│   └── payment_transaction.py    # create() override that injects fee
├── views/
│   ├── payment_provider_views.xml  # "Custom Fees" tab
│   └── payment_transaction_views.xml  # Fee fields on transaction form
└── static/src/js/
    └── payment_form.js           # Frontend badge (scaffold)
```

---

© InomERP Pvt Ltd · https://inomerp.in · info@inomerp.in
