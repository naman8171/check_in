{
    "name": "Past Work",
    "summary": "Manage and showcase past work projects on the website",
    "version": "19.0.1.0.0",
    "category": "Website",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["base", "web", "website"],
    "data": [
        "security/past_work_security.xml",
        "security/ir.model.access.csv",
        "views/past_work_category_views.xml",
        "views/past_work_tag_views.xml",
        "views/past_work_views.xml",
        "views/past_work_menus.xml",
        "views/website_past_work_templates.xml",
        "data/website_menu_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "past_work/static/src/css/past_work_backend.css",
        ],
        "web.assets_frontend": [
            "past_work/static/src/css/past_work_frontend.css",
            "past_work/static/src/js/past_work_frontend.js",
        ],
    },
    "installable": True,
    "application": True,
}
