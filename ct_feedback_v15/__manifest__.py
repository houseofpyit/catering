{
    'name': 'ct_feedback_v15',
    'version': '15.0',
    'category': '',
    'sequence': 1,
    'summary': 'Feedback',
    'author': 'Oretta Incorporation',
    'maintainer': 'Oretta Incorporation',
    'company': 'Oretta Incorporation',
    'depends' : ['base','ct_function_v15','ct_contact_v15'],
    'data' : [
        'security/ir.model.access.csv',
        'view/feedback.xml',
    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False

}