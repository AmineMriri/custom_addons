# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name' : 'Hospital Patient Portal Management',
    'summary' : 'This Module Adds Hospital Portal facility for Patients to allow access to their appointments and prescriptions',
    'description' : """
    This Module Adds Hospital Portal facility for Patients to allow access to their appointments and prescriptions
    HMS Website Portal acs hms hospital management system medical
    """,
    'version': '1.0.3',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends' : ['portal','acs_hms','website'],
    'data' : [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/email_template.xml',
        'data/data.xml',
        'views/patient_view.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/lib/Chart/Chart.js',
            'acs_hms_portal/static/src/js/portal_chart.js'
        ]
    },
    'images': [
        'static/description/hms_portal_almightycs_odoo_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 51,
    'currency': 'USD',
}
