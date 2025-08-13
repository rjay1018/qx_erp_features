# -*- coding: utf-8 -*-
{
    "name": "Customer Product Barcode",
    "version": "14.0.1.0.0",
    "summary": "Use customer-specific product barcode on Delivery Report (DR)",
    "description": "Adds a 'Customer Barcode' on products and uses it on the Delivery Slip. Falls back to internal barcode if empty.",
    "author": "QX",
    "license": "LGPL-3",    
    'category': 'Inventory', 
    "depends": ["stock", "product"],
    "data": [
        "views/product_view.xml",
    ],
    "installable": True,
    "application": False,
}
