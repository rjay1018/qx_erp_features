from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    client_barcode = fields.Char(
        'Client Barcode',
        compute='_compute_client_barcode',
        store=True
    )

    @api.depends('product_id', 'order_id.pricelist_id')
    def _compute_client_barcode(self):
        for line in self:
            # Default to product barcode
            line.client_barcode = line.product_id.barcode or ''
            if line.product_id and line.order_id.pricelist_id:
                # Search for a specific client barcode on the pricelist
                # The search is ordered to prioritize the rule on the variant over the template
                pricelist_item = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', line.order_id.pricelist_id.id),
                    ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                    '|',
                    ('product_id', '=', line.product_id.id),
                    ('product_id', '=', False),
                    ('client_barcode', '!=', False),
                    ('client_barcode', '!=', '')
                ], order='product_id desc', limit=1)

                if pricelist_item:
                    line.client_barcode = pricelist_item.client_barcode
