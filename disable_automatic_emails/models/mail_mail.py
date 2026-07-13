from odoo import api, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model
    def _disable_automatic_emails_enabled(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("disable_automatic_emails.enabled", "True")
            not in ("False", "false", "0")
        )

    @api.model
    def _disable_automatic_emails_bypassed(self):
        return bool(self.env.context.get("disable_automatic_emails_bypass"))

    def send(self, auto_commit=False, raise_exception=False):
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            self.sudo().write({"state": "cancel"})
            return True
        return super().send(auto_commit=auto_commit, raise_exception=raise_exception)

    @api.model
    def process_email_queue(self, ids=None):
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            domain = [("state", "=", "outgoing")]
            if ids:
                domain.append(("id", "in", ids))
            self.sudo().search(domain).write({"state": "cancel"})
            return True
        return super().process_email_queue(ids=ids)
