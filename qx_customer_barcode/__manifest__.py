# -*- coding: utf-8 -*-
{
    "name": "Product Customer Barcode",
    "version": "14.0.1.1.0",
    "summary": "Assigned customer barcodes to products information",
    "description": "Adds a 'Customer Barcode' on products and uses it on the Delivery Slip. Falls back to internal barcode if empty.",
    "author": "QX",
    "license": "LGPL-3",    
    'category': 'Inventory', 
    "depends": ["stock", "product"],
    "data": [
        'security/ir.model.access.csv',
        "views/customer_product_barcode_views.xml",
        "views/product_template_views.xml",
        'views/sale_order_views.xml',
        # "report/report_deliveryslip_inherit.xml",
    ],
    "installable": True,
    "application": False,
}
