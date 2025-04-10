{
    'name': 'Smart Serial Inbound Scanner',
    'version': '14.0.1.0.0',
    'summary': 'Scan and assign serial numbers efficiently during receipts',
    'depends': ['stock', 'barcodes'],
    'author': 'jaynatz',
    'category': 'Warehouse',
    'data': [
        'security/ir.model.access.csv',
        'views/serial_inbound_wizard_view.xml',
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_serial_inbound/static/src/js/serial_scanner.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
