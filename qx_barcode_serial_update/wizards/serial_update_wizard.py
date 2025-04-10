from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SerialUpdateWizard(models.TransientModel):
    _name = 'serial.update.wizard'
    _description = 'Serial Number Update Wizard'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter serial numbers separated by new lines.")
    lot_ids = fields.One2many('stock.production.lot', 'wizard_id', string='Lots')

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
                    
                    # Create or update stock quant for the lot
                    self._create_stock_quant(lot)

                    # Add the lot to the wizard's lot_ids
                    lot_ids.append(lot.id)
            
            # Clear existing lots and add the validated ones
            self.lot_ids = [(6, 0, lot_ids)]

    def _create_stock_quant(self, lot):
        """Create a stock quant for the given lot."""
        location_id = self.env.ref('stock.stock_location_stock').id
        self.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': self.product_id.id,
            'location_id': location_id,
            'lot_id': lot.id,
            'inventory_quantity': 1,
        }).action_apply_inventory()

    def write(self, vals):
        """Override write method to ensure lot_ids are cleared when scanned_serials change."""
        res = super(SerialUpdateWizard, self).write(vals)
        if 'scanned_serials' in vals:
            self.lot_ids = False
        return res