# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    customer_barcode = fields.Char(
        string="Customer Barcode",
        compute="_compute_customer_barcode",
        store=False
    )

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_customer_barcode(self):
        for line in self:
            barcode = False
            if line.product_id and line.order_id.partner_id:
                barcode_record = self.env['customer.product.barcode'].search([
                    ('product_product_id', '=', line.product_id.id),
                    ('partner_id', '=', line.order_id.partner_id.id)
                ], limit=1)
                barcode = barcode_record.barcode if barcode_record else False
            line.customer_barcode = barcode
