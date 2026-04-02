{
    "name": "HR Attendance Late Check-in Alert",
    "summary": "Highlight late check-ins and notify managers by email",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Attendances",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["hr_attendance", "mail"],
    "data": [
        "data/mail_template_data.xml",
        "views/hr_attendance_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
