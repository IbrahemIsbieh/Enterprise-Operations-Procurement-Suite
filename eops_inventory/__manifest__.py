{
    'name': 'Enterprise Inventory Integration',
    'version': '19.0.1.0.0',
    'summary': 'Integrate procurement tenders with Odoo Inventory',
    'author': 'Ibrahem Issa',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': [
        'stock',
        'purchase',
        'eops_core',
        'eops_procurement',
    ],
    'data': [
        'views/procurement_tender_views.xml',
    ],
    'installable': True,
    'application': False,
}