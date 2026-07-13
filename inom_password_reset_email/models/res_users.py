# -*- coding: utf-8 -*-

import logging

from odoo import _, models
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password(self):
        """Route the user form reset button through the EY reset sender."""
        try:
            return self.with_context(disable_automatic_emails_bypass=True)._action_reset_password()
        except MailDeliveryException as error:
            raise UserError(_("Unable to send the EY password reset email: %s", error)) from error

    def _action_reset_password(self, signup_type="reset"):
        """Send the EY-branded reset email for manual password resets."""
        if self.env.context.get("create_user") == 1 or signup_type != "reset":
            return super()._action_reset_password(signup_type=signup_type)

        if self.env.context.get("install_mode") or self.env.context.get("import_file"):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))

        self.mapped("partner_id").signup_prepare(signup_type=signup_type)
        email_values = {
            "email_cc": False,
            "auto_delete": True,
            "message_type": "user_notification",
            "recipient_ids": [],
            "partner_ids": [],
            "scheduled_date": False,
        }
        template_view = self.env.ref("auth_signup.reset_password_email")

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))

            user_lang = user.lang or self.env.lang or "en_US"
            body = self.env["mail.render.mixin"].with_context(lang=user_lang)._render_template(
                template_view,
                model="res.users",
                res_ids=user.ids,
                engine="qweb_view",
                options={"post_process": True},
            )[user.id]

            with self.env.cr.savepoint():
                mail = self.env["mail.mail"].sudo().with_context(
                    disable_automatic_emails_bypass=True,
                ).create({
                    "subject": self.with_context(lang=user_lang).env._("Reset your EY account password"),
                    "email_from": user.company_id.email_formatted or user.email_formatted,
                    "body_html": body,
                    "email_to": user.email,
                    **email_values,
                })
                mail.with_context(disable_automatic_emails_bypass=True).send(raise_exception=True)

            _logger.info("EY password reset email sent for user <%s> to <%s>", user.login, user.email)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Notification"),
                "message": _("A reset password link was sent by email"),
                "sticky": False,
            },
        }
