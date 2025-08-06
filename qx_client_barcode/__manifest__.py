{
    'name': 'Client Specific Product Barcode',
    'version': '14.0.1.0.0',
    'summary': 'Enable client-specific product barcodes using the pricelist',
    'description': """
        This module allows setting a specific barcode for a product on a client's pricelist.
        This barcode is then displayed on Sales Orders and Delivery Slips.
    """,
    'author': 'Qx',
    'website': '',
    'category': 'Sales',
    'depends': ['sale_management', 'stock'],
    'data': [
        'views/product_pricelist_item_views.xml',
        'views/sale_order_views.xml',
        'views/stock_move_views.xml',
        'views/report_deliveryslip.xml',
    ],
    'installable': True,
    'application': False,
}
