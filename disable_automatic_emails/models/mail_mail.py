from odoo import api, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model
    def _disable_automatic_emails_enabled(self):
        return self.env["ir.mail_server"]._disable_automatic_emails_enabled()

    @api.model
    def _disable_automatic_emails_bypassed(self):
        return self.env["ir.mail_server"]._disable_automatic_emails_bypassed()

    @api.model_create_multi
    def create(self, vals_list):
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            return self.browse()
        return super().create(vals_list)

    def send(self, auto_commit=False, raise_exception=False, post_send_callback=None):
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            self.sudo().filtered(lambda mail: mail.state == "outgoing").write({"state": "cancel"})
            if post_send_callback:
                post_send_callback(self.ids)
            return True
        return super().send(
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            post_send_callback=post_send_callback,
        )

    @api.model
    def process_email_queue(self, ids=None, batch_size=1000):
        if (
            self._disable_automatic_emails_enabled()
            and not self._disable_automatic_emails_bypassed()
        ):
            domain = [("state", "=", "outgoing")]
            if ids:
                domain.append(("id", "in", ids))
            self.sudo().search(domain, limit=batch_size).write({"state": "cancel"})
            return True
        return super().process_email_queue(ids=ids, batch_size=batch_size)
