{
    'name': 'Enterprise Procurement Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage supplier quotations and procurement comparisons',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'category': 'Operations',
    'depends': [
        'base',
        'mail',
        'purchase',
        'eops_core',
        'eops_purchase_request',
    ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/procurement_tender_views.xml',
    ],
    'installable': True,
    'application': True,
}
