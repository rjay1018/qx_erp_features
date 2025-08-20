# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomerProductBarcode(models.Model):
    _name = "customer.product.barcode"
    _description = "Customer Product Barcode"
    _rec_name = "barcode"

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True,
        ondelete="cascade"
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string="Product Template",
        required=True,
        ondelete="cascade"
    )
    product_product_id = fields.Many2one(
        'product.product',
        string="Product Variant",
        ondelete="cascade"
    )
    barcode = fields.Char(string="Customer Barcode", required=True)

    _sql_constraints = [
        (
            "barcode_partner_product_unique",
            "unique(partner_id, product_product_id)",
            "A customer barcode must be unique per customer and product variant."
        ),
    ]

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """Autofill product_product_id if only one variant exists."""
        for rec in self:
            rec.product_product_id = False
            if rec.product_tmpl_id:
                variants = rec.product_tmpl_id.product_variant_ids
                if len(variants) == 1:
                    rec.product_product_id = variants[0].id

    @api.model
    def create(self, vals):
        """Ensure product_tmpl_id syncs with product_product_id."""
        if vals.get("product_product_id") and not vals.get("product_tmpl_id"):
            product = self.env["product.product"].browse(vals["product_product_id"])
            vals["product_tmpl_id"] = product.product_tmpl_id.id
        return super().create(vals)

    def write(self, vals):
        """Keep product_tmpl_id in sync when product_product_id changes."""
        if vals.get("product_product_id"):
            product = self.env["product.product"].browse(vals["product_product_id"])
            vals["product_tmpl_id"] = product.product_tmpl_id.id
        return super().write(vals)
