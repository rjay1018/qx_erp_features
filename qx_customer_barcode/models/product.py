# models/product_template.py
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    customer_barcode_ids = fields.One2many(
        'customer.product.barcode',
        'product_tmpl_id',
        string="Customer Barcodes"
    )
    customer_barcode_count = fields.Integer(
        string="Customer Barcode Count",
        compute="_compute_customer_barcode_count"
    )

    def _compute_customer_barcode_count(self):
        for product in self:
            product.customer_barcode_count = len(product.customer_barcode_ids)

    def action_open_customer_barcodes(self):
        """Button action to open customer barcodes for this product."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Barcodes',
            'res_model': 'customer.product.barcode',
            'view_mode': 'tree,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {'default_product_tmpl_id': self.id},
        }