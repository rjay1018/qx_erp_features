# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = "product.product"

    client_barcode711 = fields.Char("711 Barcode", help="711-specific barcode for this product.")
