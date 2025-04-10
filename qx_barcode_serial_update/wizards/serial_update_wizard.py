from odoo import models, fields, api, _ 
from odoo.exceptions import UserError 
 
class SerialUpdateWizard(models.TransientModel): 
    _name = 'serial.update.wizard' 
    _description = 'Serial Number Update Wizard' 
 
    product_id = fields.Many2one('product.product', string='Product', required=True) 
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter serial numbers separated by new lines.") 
    lot_ids = fields.Many2many('stock.production.lot', string='Lots', readonly=True) 
 
    @api.onchange('scanned_serials') 
    def _onchange_scanned_serials(self): 
        """Process scanned serials and validate them.""" 
        if self.scanned_serials: 
            serial_lines = self.scanned_serials.split('\n') 
            lot_ids = [] 
            for serial in serial_lines: 
                serial = serial.strip() 
                if serial: 
                    lot = self.env['stock.production.lot'].search([ 
                        ('name', '=', serial), 
                        ('product_id', '=', self.product_id.id) 
                    ], limit=1) 
                    if not lot: 
                        raise UserError(_("Serial number '%s' does not exist for this product.") % serial) 
                    lot_ids.append(lot.id) 
            self.lot_ids = [(6, 0, lot_ids)] 
 
    def update_quantity(self): 
        """Update the quantity based on the scanned serials.""" 
        if not self.lot_ids: 
            raise UserError(_("No valid serial numbers found to update quantity.")) 
 
        # Assuming the product is tracked by serial numbers 
        location_id = self.env.ref('stock.stock_location_stock').id 
        for lot in self.lot_ids: 
            self.env['stock.quant'].with_context(inventory_mode=True).create({ 
                'product_id': self.product_id.id, 
                'location_id': location_id, 
                'lot_id': lot.id, 
                'inventory_quantity': 1, 
            }).action_apply_inventory() 
 
        return { 
            'type': 'ir.actions.client', 
            'tag': 'display_notification', 
            'params': { 
                'title': _('Success'), 
                'message': _('Quantity updated successfully for %d serials.') % len(self.lot_ids), 
                'sticky': False, 
            } 
        } 
