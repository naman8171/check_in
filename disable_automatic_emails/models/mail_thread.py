from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_record_by_email(self, message, recipients_data, msg_vals=False, **kwargs):
        if (
            self.env["mail.mail"]._disable_automatic_emails_enabled()
            and not self.env["mail.mail"]._disable_automatic_emails_bypassed()
        ):
            return True
        return super()._notify_record_by_email(
            message,
            recipients_data,
            msg_vals=msg_vals,
            **kwargs,
        )
