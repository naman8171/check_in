from odoo import models


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    def _compute_feature_support_fields(self):
        """Ensure Stripe exposes fee configuration and tokenization support.

        Odoo's checkout and invoice payment widgets already consume provider fee
        settings (domestic/international variable + fixed fee). This module makes
        sure Stripe enables those capabilities so fees are applied consistently in:
        - eCommerce checkout
        - invoice "Pay" modal (payment link)
        - resulting payment transactions
        """
        super()._compute_feature_support_fields()
        for provider in self.filtered(lambda p: p.code == "stripe"):
            if hasattr(provider, "support_fees"):
                provider.support_fees = True
            if hasattr(provider, "support_tokenization"):
                provider.support_tokenization = True

    def _get_compatible_providers(self, company_id, partner_id, amount, currency_id=None, force_tokenization=False, is_express_checkout=False, is_validation=False, report=None, **kwargs):
        """Delegate to core logic; hook kept for module-level extensibility.

        Keeping this override allows safe extension points in this dedicated module
        without touching the base Stripe provider implementation.
        """
        return super()._get_compatible_providers(
            company_id=company_id,
            partner_id=partner_id,
            amount=amount,
            currency_id=currency_id,
            force_tokenization=force_tokenization,
            is_express_checkout=is_express_checkout,
            is_validation=is_validation,
            report=report,
            **kwargs,
        )
