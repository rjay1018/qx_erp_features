from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    client_barcode = fields.Char(
        'Client Barcode',
        compute='_compute_client_barcode',
        store=True
    )

    @api.depends('product_id', 'picking_id.partner_id', 'sale_line_id.client_barcode')
    def _compute_client_barcode(self):
        for move in self:
            # Default to product barcode
            barcode = move.product_id.barcode or ''

            # If linked to a sale order line, just copy its client barcode
            if move.sale_line_id and move.sale_line_id.client_barcode:
                barcode = move.sale_line_id.client_barcode
            # If not from a sale order, try to find from partner's pricelist
            elif move.product_id and move.picking_id.partner_id:
                partner = move.picking_id.partner_id
                if partner.property_product_pricelist:
                    pricelist = partner.property_product_pricelist

                    pricelist_item = self.env['product.pricelist.item'].search([
                        ('pricelist_id', '=', pricelist.id),
                        ('product_tmpl_id', '=', move.product_id.product_tmpl_id.id),
                        '|',
                        ('product_id', '=', move.product_id.id),
                        ('product_id', '=', False),
                        ('client_barcode', '!=', False),
                        ('client_barcode', '!=', '')
                    ], order='product_id desc', limit=1)

                    if pricelist_item:
                        barcode = pricelist_item.client_barcode

            move.client_barcode = barcode
