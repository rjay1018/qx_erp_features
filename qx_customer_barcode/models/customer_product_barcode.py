from odoo import models, fields

class CustomerProductBarcode(models.Model):
    _name = "customer.product.barcode"
    _description = "Customer Product Barcode"
    _rec_name = "barcode"

    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    product_tmpl_id = fields.Many2one("product.template", string="Product", required=True)
    barcode = fields.Char(string="Customer Barcode", required=True)
