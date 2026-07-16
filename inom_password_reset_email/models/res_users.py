# -*- coding: utf-8 -*-

import logging

from odoo import _, models
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Maps an internal "flow" key to everything needed to send its EY branded
# email. New flows (invoice_email, etc.) just need a new entry here + a
# matching inom.notification.template registry record with the same
# technical_key.
_EY_FLOWS = {
    "reset": {
        "technical_key": "password_reset",
        "view_xmlid": "auth_signup.reset_password_email",
        "subject": "Reset your EY account password",
        "notification_message": "A reset password link was sent by email",
        "log_label": "password reset",
    },
    "signup": {
        "technical_key": "welcome_email",
        "view_xmlid": "inom_password_reset_email.welcome_email_view",
        "subject": "Welcome to EY - set your account password",
        "notification_message": "A welcome email with a set-password link was sent",
        "log_label": "welcome",
    },
}


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_reset_password(self):
        """Route both the manual reset button and new-user invitation
        emails through the EY branded sender (when enabled in Settings).

        Note: the disable_automatic_emails bypass is applied further down,
        only once we've confirmed the relevant custom template is actually
        enabled in Settings > EY Notifications. Otherwise stock Odoo
        behavior (including disable_automatic_emails' suppression) is
        preserved.
        """
        try:
            return self._action_reset_password()
        except MailDeliveryException as error:
            raise UserError(_("Unable to send the EY notification email: %s", error)) from error

    def _action_reset_password(self, signup_type="reset"):
        """Send the EY-branded reset or welcome email, whichever applies."""
        # `create_user` is the context flag Odoo core has always used to
        # mark the "new user / invitation" flow, independently of whatever
        # literal signup_type string a given Odoo version passes through -
        # so we key off that first, and only fall back to the signup_type
        # argument for anything else.
        if self.env.context.get("create_user"):
            flow = "signup"
        elif signup_type == "reset":
            flow = "reset"
        else:
            # Unknown/unsupported signup_type (e.g. portal 'signup') ->
            # never touched by this module, always stock Odoo behavior.
            return super()._action_reset_password(signup_type=signup_type)

        config = _EY_FLOWS[flow]

        if self.env.context.get("install_mode") or self.env.context.get("import_file"):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))

        if not self.env["inom.notification.template"].is_template_enabled(config["technical_key"]):
            # Master toggle is off, or this particular template wasn't
            # picked in Settings > EY Notifications -> stock Odoo behavior.
            return super()._action_reset_password(signup_type=signup_type)

        self.mapped("partner_id").signup_prepare(signup_type=signup_type)
        email_values = {
            "email_cc": False,
            "auto_delete": True,
            "message_type": "user_notification",
            "recipient_ids": [],
            "partner_ids": [],
            "scheduled_date": False,
        }
        template_view = self.env.ref(config["view_xmlid"])

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))

            user_lang = user.lang or self.env.lang or "en_US"

            # Generate reset/signup URL
            signup_url = user.partner_id._get_signup_url()

            body = self.env["mail.render.mixin"].with_context(
                lang=user_lang,
                signup_url=signup_url,
            )._render_template(
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
                    "subject": self.with_context(lang=user_lang).env._(config["subject"]),
                    "email_from": user.company_id.email_formatted or user.email_formatted,
                    "body_html": body,
                    "email_to": user.email,
                    **email_values,
                })
                mail.with_context(disable_automatic_emails_bypass=True).send(raise_exception=True)

            _logger.info(
                "EY %s email sent for user <%s> to <%s>",
                config["log_label"], user.login, user.email,
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Notification"),
                "message": _(config["notification_message"]),
                "sticky": False,
            },
        }
