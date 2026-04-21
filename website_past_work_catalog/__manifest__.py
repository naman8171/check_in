{
    "name": "Website Past Work Catalog",
    "summary": "Dynamic, spreadsheet-driven past work catalog with dual filters",
    "version": "17.0.1.0.0",
    "category": "Website",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["website"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/website_past_work_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_past_work_catalog/static/src/scss/past_work_catalog.scss",
            "website_past_work_catalog/static/src/js/past_work_catalog.js",
        ],
    },
    "installable": True,
    "application": False,
}
