# -*- coding: utf-8 -*-
{
    "name": "EY Password Reset Email",
    "summary": "Replace the default user password reset email with EY-branded content.",
    "version": "18.0.1.0.0",
    "category": "Administration",
    "author": "EY",
    "license": "LGPL-3",
    "depends": ["auth_signup", "mail", "disable_automatic_emails"],
    "data": [
        "data/password_reset_template.xml",
    ],
    "installable": True,
    "application": False,
}
