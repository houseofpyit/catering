{
    'name': 'ct_website_v15',
    'version': '15.0',
    'category': '',
    'summary': 'Master',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends': ['base','ct_inventory_v15'],
    'data': [  
        'security/ir.model.access.csv',
        'view/inherit_company.xml',
        'view/package_master.xml',
        'view/gallery_master.xml',
        'view/season_master.xml',
        'view/season_recipe.xml',
        'view/websit_category.xml',
        'view/menu.xml',
    ],    
    'installable': True,
    'application':True,
    'auto_install': False
}
