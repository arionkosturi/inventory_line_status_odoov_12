{
    'name': 'Inventory Line Status',
    'version': '12.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Add status tracking to inventory lines',
    'sequence': 100,
    'license': 'LGPL-3',
    'author': 'Arion Kosturi',
    'website': 'www.github.com/arionkosturi',
    'depends': ['stock', 'web'],
    'data': [
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'data/ir_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'inventory_line_status/static/src/js/status_handler.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
