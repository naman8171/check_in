from odoo import api, models


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

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

    def send_email(self, message, mail_server_id=False, smtp_server=False, smtp_port=False,
                   smtp_user=False, smtp_password=False, smtp_encryption=False,
                   smtp_ssl_certificate=False, smtp_ssl_private_key=False,
                   smtp_debug=False, smtp_session=None):
        """Stop the final SMTP hand-off for every Odoo-generated email.

        Password reset and new-device emails in Odoo 18 can create a ``mail.mail``
        record directly and call ``mail.mail.send()`` immediately.  Guarding the
        mail server is therefore the last line of defense: every standard Odoo
        outgoing email reaches this method immediately before SMTP delivery.
        """
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            return False
        return super().send_email(
            message,
            mail_server_id=mail_server_id,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            smtp_encryption=smtp_encryption,
            smtp_ssl_certificate=smtp_ssl_certificate,
            smtp_ssl_private_key=smtp_ssl_private_key,
            smtp_debug=smtp_debug,
            smtp_session=smtp_session,
        )
