{
    'name': 'ct_menu_v15',
    'version': '15.0',
    'category': '',
    'sequence': 1,
    'summary': 'Menu',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends': ['base','ct_inventory_v15','ct_report_v15','ct_function_v15','ct_contact_v15','sale','stock','sales_team'],
    'data': [  
        'security/ir.model.access.csv',
        'security/security_group.xml',
        'view/main_menu.xml',
    ],    
    'installable': True,
    'application':True,
    'auto_install': False
}
