{
    "name": "Module Explanation Performance Tracker",
    "summary": "Track assignment, explanations, effort, and employee performance for Odoo module explanation sessions",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["hr", "mail"],
    "data": [
        "security/module_explanation_security.xml",
        "security/ir.model.access.csv",
        "data/module_explanation_sequence.xml",
        "views/module_explanation_activity_views.xml",
        "views/hr_employee_views.xml",
        "views/module_explanation_menus.xml",
    ],
    "installable": True,
    "application": True,
}
