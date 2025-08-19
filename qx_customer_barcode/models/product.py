from odoo import models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_open_customer_barcodes(self):
        self.ensure_one()
        return {
            "name": "Customer Barcodes",
            "type": "ir.actions.act_window",
            "res_model": "customer.product.barcode",
            "view_mode": "tree,form",
            "domain": [("product_tmpl_id", "=", self.id)],
            "context": {"default_product_tmpl_id": self.id},
        }
