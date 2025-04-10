{ 
    'name': 'Serial Number Inbound Update', 
    'version': '1.0', 
    'category': 'Inventory', 
    'summary': 'Allows updating serial numbers/lots for products via barcode scanning', 
    'description': ''' 
        This module adds functionality to update serial numbers or lots for products 
        using a wizard launched from the product form. 
    ''', 
    'author': 'jaynatz', 
    'depends': ['stock', 'product'], 
    'data': [ 
        'security/ir.model.access.csv',
        'views/product_views.xml', 
        'wizards/serial_update_wizard.xml', 
    ],
    'assets': {
        'web.assets_backend': [
            'qx_barcode_serial_update/static/src/js/barcode_scanner.js',
        ],
    },
    'installable': True, 
    'application': False, 
} 
