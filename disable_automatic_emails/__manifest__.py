{
    "name": "Disable Automatic Emails",
    "summary": "Disable automatically triggered outgoing emails while allowing explicit opt-in sends.",
    "version": "18.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["mail"],
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
