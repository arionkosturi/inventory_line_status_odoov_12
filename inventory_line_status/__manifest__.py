{
    'name': 'Inventory Line Status',
    'version': '12.0.1.0.0',
    'summary': 'Add status tracking to inventory lines',
    'description': """
        Track status of inventory operation lines with visual indicators:
        - ? (Blue) - Not yet processed
        - ⚠ (Yellow) - Unchecked
        - ✓ (Green) - Checked

        Features:
        - Individual line status toggle
        - Bulk initialization of unprocessed lines
        - Status filters and grouping
        - Available in both Operations and Detailed Operations tabs
        - Tooltips for status buttons
        - Color-coded row backgrounds
        - Status synchronization between moves and lines
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
