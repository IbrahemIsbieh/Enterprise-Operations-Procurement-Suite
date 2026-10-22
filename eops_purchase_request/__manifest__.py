{
    'name': 'Enterprise Purchase Requests',
    'version': '19.0.1.0.0',
    'summary': 'Purchase requests and approval workflow',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'category': 'Operations',
    'depends': [
        'base',
        'mail',
        'purchase',
        'stock',
        'eops_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/purchase_request_views.xml',
    ],
    'installable': True,
    'application': True,
}