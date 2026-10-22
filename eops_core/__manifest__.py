{
    'name': 'Enterprise Operations Core',
    'version': '19.0.1.0.0',
    'summary': 'Core departments and approval policies',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'category': 'Operations',
    'depends': ['base', 'mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/department_views.xml',
        'views/approval_policy_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}