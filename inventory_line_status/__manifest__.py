{
    'name': 'Inventory Line Status',
    'version': '12.0.1.0.0',
    'summary': 'Add check status to inventory lines',
    'description': """
        Simple status tracking for inventory operations:
        - ✓ Checked
        - ⚠ Unchecked

        Available in both Operations and Detailed Operations tabs.
    """,
    'category': 'Inventory',
    'author': 'Custom',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
