{
    'name': 'Whatsapp Connector',
    'version': '15.0',
    'category': '',
    'sequence': 1,
    'summary': 'Master',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends': ['base','ct_contact_v15'],
    'data': [  
        'security/ir.model.access.csv',

        # 'data/sequence.xml',
        
        # 'wizards/add_utensils.xml',
        
        # 'report/all_po_prints.xml',
        
        'views/inherit_res_company.xml',
        'views/inherit_purchase.xml',
        ],

    'installable': True,
    'application':True,
    'auto_install': False
}
