from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, email_layout_xmlid=False):
        if (
            self.env["mail.mail"]._disable_automatic_emails_enabled()
            and not self.env["mail.mail"]._disable_automatic_emails_bypassed()
        ):
            return False
        return super().send_mail(
            res_id,
            force_send=force_send,
            raise_exception=raise_exception,
            email_values=email_values,
            email_layout_xmlid=email_layout_xmlid,
        )

    def send_mail_batch(self, res_ids, force_send=False, raise_exception=False, email_values=None, email_layout_xmlid=False):
        if (
            self.env["mail.mail"]._disable_automatic_emails_enabled()
            and not self.env["mail.mail"]._disable_automatic_emails_bypassed()
        ):
            return {res_id: False for res_id in res_ids}
        return super().send_mail_batch(
            res_ids,
            force_send=force_send,
            raise_exception=raise_exception,
            email_values=email_values,
            email_layout_xmlid=email_layout_xmlid,
        )
