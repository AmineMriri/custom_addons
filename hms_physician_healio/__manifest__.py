# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'PHYSICIAN HEALIO',
    'version': '1.0',
    'category': 'Web services / Mobile / Santé',
    'sequence': 15,
    'summary': 'Track leads and close opportunities',
    'description': "",
    'website': 'https://www.targa-consult.com',
    'depends': [
        'acs_hms'
    ],
    'data': [
        'views/hms_physician_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
