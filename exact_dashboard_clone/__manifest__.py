{
    "name": "Exact Dashboard Clone",
    "summary": "Standalone dashboard/form/email workflow module",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/mail_template.xml",
        "views/clone_record_views.xml",
        "views/menus.xml",
    ],
    "application": True,
    "installable": True,
}
