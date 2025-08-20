# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerProductBarcode(models.Model):
    _name = "customer.product.barcode"
    _description = "Customer Product Barcode"

    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    product_tmpl_id = fields.Many2one('product.template', string="Product Template", required=True)
    product_product_id = fields.Many2one('product.product', string="Product Variant")
    barcode = fields.Char(string="Customer Barcode", required=True)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """
        Autofill product_product_id based on product_tmpl_id.
        If template has only one variant, assign it automatically.
        """
        for rec in self:
            rec.product_product_id = False
            if rec.product_tmpl_id:
                variants = rec.product_tmpl_id.product_variant_ids
                if len(variants) == 1:
                    rec.product_product_id = variants[0].id
