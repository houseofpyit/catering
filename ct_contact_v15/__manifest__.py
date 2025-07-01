{
    'name': 'ct_contact_v15',
    'version': '15.0',
    'category': '',
    'sequence': 1,
    'summary': 'Master',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends': ['base','contacts','web','sale','purchase','sms','portal','purchase_stock'],
    'data': [  
        'data/data.xml',
        'security/ir.model.access.csv',
        'view/inherit_contact.xml',
        'view/inherit_company.xml',
        'view/category.xml',
        # 'view/main_menu.xml',
          ],    
    'assets':{
        'web.assets_backend': [
            'ct_contact_v15/static/src/css/custome_group.css',
            ],
    },
    'installable': True,
    'application':True,
    'auto_install': False
}
