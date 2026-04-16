# Payment Stripe Extra Fees — Odoo 19 Enterprise

## Overview
Adds configurable **Domestic** and **International** extra fees to the Stripe payment provider in Odoo 19 Enterprise, matching the native Stripe Fees tab UI.

---

## Features
| Feature | Description |
|---|---|
| **Add Extra Fees toggle** | Enable/disable fee collection per provider |
| **Stripe Fee Product** | Auto-created `[STRIPE_FEE] Stripe Fee` service product |
| **Fixed Domestic Fee** | Flat amount added to domestic transactions |
| **Variable Domestic Fee %** | Percentage of cart total added to domestic transactions |
| **Free Domestic Fees Threshold** | Waive fees when cart exceeds a set amount |
| **Fixed International Fee** | Flat amount for cross-border transactions |
| **Variable International Fee %** | Percentage for cross-border transactions |
| **Free International Fees Threshold** | Waive international fees above a set amount |
| **Fee Line on Sale Order** | Fee added as order line after payment confirmed |
| **Fee Line on Invoice** | Fee added as invoice line after payment confirmed |
| **Frontend Fee Notice** | Customer sees fee preview at checkout |

---

## Installation

1. Copy `payment_stripe_extra_fees/` to your Odoo addons directory:
   ```
   /path/to/odoo/addons/payment_stripe_extra_fees/
   ```

2. Update the addons list:
   ```bash
   ./odoo-bin -u payment_stripe_extra_fees -d your_database
   ```
   Or via the UI: **Settings → Activate Developer Mode → Apps → Update Apps List**

3. Search for **"Stripe Payment Extra Fees"** and install.

---

## Configuration

1. Go to **Accounting → Configuration → Payment Providers**
2. Open your **Stripe** provider
3. Click the **"Stripe Fees"** tab
4. Enable **"Add Extra Fees"**
5. Configure:
   - **Stripe Fee Product**: auto-filled as `[STRIPE_FEE] Stripe Fee`
   - **Fixed/Variable Domestic Fees**
   - **Fixed/Variable International Fees**
   - **Threshold amounts** for fee waivers

---

## How Fees Work

### Domestic vs International
- **Domestic**: Customer country == Company country
- **International**: Customer country ≠ Company country

### Fee Formula
```
Total Fee = Fixed Fee + (Amount × Variable Fee %)
```
If `Free above` is checked and cart total ≥ threshold → **fee = 0**

### Example (matching the screenshot)
| Setting | Value |
|---|---|
| Fixed Domestic Fee | 5.00 |
| Variable Domestic Fee | 0.00% |
| Free Domestic if above | ✅ 100.00 |
| Fixed International Fee | 7.00 |
| Variable International Fee | 0.00% |
| Free International if above | ✅ 150.00 |

- Cart = 80.00 (domestic) → Fee = **5.00**
- Cart = 120.00 (domestic) → Fee = **0.00** (above threshold)
- Cart = 130.00 (international) → Fee = **7.00**
- Cart = 160.00 (international) → Fee = **0.00** (above threshold)

---

## Dependencies
- `payment_stripe` (Odoo Enterprise)
- `sale_management`
- `account`

---

## License
LGPL-3
