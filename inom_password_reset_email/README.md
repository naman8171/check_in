# EY Password Reset Email

This Odoo 18 Community module replaces the standard password reset email template used by **Settings → Users → Reset Password** with a fully EY-branded template.

## Features

- Overrides the `auth_signup.reset_password_email` QWeb email view.
- Removes default product branding and references from the email body and footer.
- Adds EY colors, company name, the configured company logo, and custom password reset copy.
- Keeps the standard reset token generation intact while sending an EY-specific subject and email body.
- Routes the user form reset action through the custom sender and bypasses `disable_automatic_emails` only for this password reset email, so default automatic emails remain disabled.

## Installation

1. Copy this directory into your Odoo addons path.
2. Update the Apps list.
3. Install **EY Password Reset Email**.
4. Go to **Settings → Users**, open a user, and click **Reset Password**.

