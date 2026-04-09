{
    'name': 'Technical Dossier',
    'version': '1.0',
    'depends': [
        'base',
        'inom_delivery_picking_service'
    ],
    'data': [
        'security/ir.model.access.csv', 
        'report/paperformat.xml',    
        'report/technical_dossier_report.xml',
        'report/technical_dossier_template.xml',
        'views/technical_dossier_views.xml',
        'views/import_line_wizard_view.xml',
	    'views/res_config_settings_view.xml',
        'data/dossier.xml',
    ],
    'installable': True,
    'application': True,
}
