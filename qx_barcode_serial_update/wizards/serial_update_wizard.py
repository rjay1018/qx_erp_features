from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SerialUpdateWizard(models.TransientModel):
    _name = 'serial.update.wizard'
    _description = 'Serial Number Update Wizard'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        domain="[('usage', '=', 'internal')]",
        required=True,
        help="Select the stock location where the serials will be stored."
    )
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter serial numbers separated by new lines.")
    lot_ids = fields.One2many('stock.production.lot', 'wizard_id', string='Valid Serials')
    invalid_serials = fields.Text(string='Invalid/Duplicate Serials', readonly=True)

    @api.onchange('scanned_serials')
    def _onchange_scanned_serials(self):
        """Process scanned serials and validate them."""
        if self.scanned_serials:
            serial_lines = self.scanned_serials.split('\n')
            valid_lots = []
            invalid_serials = []

            for serial in serial_lines:
                serial = serial.strip()
                if not serial:
                    continue

                # Check for duplicates
                if serial in [lot.name for lot in self.lot_ids]:
                    invalid_serials.append(f"Duplicate: {serial}")
                    continue

                # Validate serial
                lot = self.env['stock.production.lot'].search([
                    ('name', '=', serial),
                    ('product_id', '=', self.product_id.id)
                ], limit=1)
                if not lot:
                    invalid_serials.append(serial)
                    continue

                # Link lot to wizard
                lot.write({'wizard_id': self.id})
                valid_lots.append(lot.id)

            # Update lots and invalid serials
            self.lot_ids = [(6, 0, valid_lots)]
            self.invalid_serials = '\n'.join(invalid_serials) if invalid_serials else False

            # Notify user about invalid/duplicate serials
            if invalid_serials:
                raise UserError(_("The following serials are invalid or duplicated:\n%s") % '\n'.join(invalid_serials))

            # Batch-create stock quants for valid lots
            self._create_stock_quant(valid_lots)

    def _create_stock_quant(self, lot_ids):
        """Batch-create stock quants for the given lots at the selected location."""
        lots = self.env['stock.production.lot'].browse(lot_ids)
        self.env['stock.quant'].create([{
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,  # Use the selected location
            'lot_id': lot.id,
            'inventory_quantity': 1,
        } for lot in lots]).action_apply_inventory()

    def generate_summary_report(self):
        """Generate a summary report of processed serials."""
        total_serials = len(self.scanned_serials.split('\n')) if self.scanned_serials else 0
        valid_serials = len(self.lot_ids)
        invalid_serials = len(self.invalid_serials.split('\n')) if self.invalid_serials else 0

        message = f"""
        Summary Report:
        ----------------
        Total Serials Scanned: {total_serials}
        Valid Serials: {valid_serials}
        Invalid/Duplicate Serials: {invalid_serials}
        Stock Location: {self.location_id.display_name}
        """
        return self.env['bus.bus']._sendone(self.env.user.partner_id, 'snackbar', {'message': message})

    @api.model
    def unlink(self):
        """Clean up temporary data when the wizard is closed."""
        for wizard in self:
            wizard.lot_ids.write({'wizard_id': False})
        return super(SerialUpdateWizard, self).unlink()