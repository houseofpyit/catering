{
    'name': 'Logout Idle User',
    'version': '15.0',
    'summary': """Auto logout idle user with fixed time""",
    'description': """User can fix the timer in the user's profile, if the user
     is in idle mode the user will logout from session automatically """,
    'category': 'Extra Tools',
    'author': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/res_users_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/auto_logout_idle_user_odoo/static/src/xml/systray.xml',
            '/auto_logout_idle_user_odoo/static/src/js/systray.js',
            '/auto_logout_idle_user_odoo/static/src/css/systray.css'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
