{
    'name': 'Inventory Line Status',
    'version': '12.0.1.0.0',
    'summary': 'Easy status tracking for inventory lines',
    'description': """
        Simple one-click status tracking for inventory operations:

        Features:
        - Quick toggle buttons to mark items as checked/unchecked
        - Status syncs between Operations and Detailed Operations
        - Color-coded rows for easy status identification
        - Works in all operation types (Receipts, Transfers, Deliveries)
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
