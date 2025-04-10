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
                if serial in [lot.name for lot in self.env['stock.production.lot'].browse(valid_lots)]:
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

                valid_lots.append(lot.id)

            # Notify user about invalid/duplicate serials
            if invalid_serials:
                raise UserError(_("The following serials are invalid or duplicated:\n%s") % '\n'.join(invalid_serials))

            # Store valid lots in the context for later use
            self._context.update({'valid_lot_ids': valid_lots})

    def action_create_stock_quants(self):
        """Create stock quant records for valid serials at the selected location."""
        valid_lot_ids = self._context.get('valid_lot_ids', [])
        lots = self.env['stock.production.lot'].browse(valid_lot_ids)

        if not lots:
            raise UserError(_("No valid serials found to create stock quants."))

        for lot in lots:
            # Use _update_available_quantity to create/update stock.quant
            self.env['stock.quant']._update_available_quantity(
                product_id=self.product_id,
                location_id=self.location_id,
                quantity=1,
                lot_id=lot
            )

        # Provide feedback to the user
        message = f"""
        Stock Quant Creation Successful:
        -------------------------------
        Total Serials Scanned: {len(self.scanned_serials.splitlines())}
        Valid Serials Processed: {len(lots)}
        Stock Location: {self.location_id.display_name}
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'sticky': False,
            }
        }