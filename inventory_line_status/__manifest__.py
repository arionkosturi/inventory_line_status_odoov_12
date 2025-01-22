{
    'name': 'Inventory Line Status',
    'version': '12.0.1.0.0',
    'summary': 'Add status tracking to inventory lines',
    'description': """
        Track status of inventory operation lines:
        - ❓ Not Processed (Blue)
        - ⚠ Unchecked (Yellow)
        - ✓ Checked (Green)

        Features:
        - Individual line status toggle
        - Bulk initialization of unprocessed lines
        - Status filters and grouping
        - Available in both Operations and Detailed Operations tabs
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
    'auto_install': False,
}
