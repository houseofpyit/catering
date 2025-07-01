# -*- coding: utf-8 -*-
{
    'name': 'Restrict Concurrent User Logins',
    'version': '15.0',
    'summary': 'Restrict concurrent sessions, User force logout, Automatic session expiry',
    'description': 'Restrict concurrent sessions, User force logout, Automatic session expiry',
    'author': 'Livedigital Technologies Private Limited',
    'company': 'Livedigital Technologies Private Limited',
    'maintainer': 'Livedigital Technologies Private Limited',
    'website': 'https://ldtech.in',
    'depends': ['base'],
    'data': [
        'views/res_users_view.xml',
        'views/templates.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

# Werkzeug==0.11.15
