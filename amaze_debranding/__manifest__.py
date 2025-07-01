{
    'name': 'AMAZE Debranding',
    'version': '15.0',
    'category': '',
    'sequence': 1,
    'summary': 'Master',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends': ['base','web'],
    'data': [  
        # 'security/ir.model.access.csv',
        'views/webclient_temp.xml',
          ],    
    # 'assets': {
    #     'web.assets_backend': [
    #         'amaze_debranding/static/src/js/app_window_title.js',
    #     ],
    # },
    'installable': True,
    'application':True,
    'auto_install': False
}
