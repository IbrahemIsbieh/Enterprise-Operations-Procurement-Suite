{
    'name': 'Enterprise Finance Integration',
    'version': '19.0.1.0.0',
    'summary': 'Track vendor bills linked to procurement tenders',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'depends': [
        'account',
        'purchase',
        'eops_core',
        'eops_procurement',
        'eops_inventory',
    ],
    'data': [
        'views/procurement_tender_views.xml',
    ],
    'installable': True,
    'application': False,
}