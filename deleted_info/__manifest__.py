{
    'name': "Track Deleted Records",
    'summary': """
        View deleted records.""",
    'description': """
        Admin users can see which records have been deleted and by whom.
    """,
    'author': 'Oretta Incorporation',
    'category': 'Extra Tools',
    'version': '14.0',
    'depends': ['base_setup'],
    'data': [
        'security/deleted_records_security.xml',
        'security/ir.model.access.csv',
        'views/deleted_records_views.xml',
        'wizard/delete_records_upto_wizard_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
