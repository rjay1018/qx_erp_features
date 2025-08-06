from odoo import models, fields

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    client_barcode = fields.Char('Client Barcode')
