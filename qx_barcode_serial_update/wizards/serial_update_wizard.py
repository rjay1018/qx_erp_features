from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SerialUpdateWizard(models.TransientModel):
    _name = 'serial.update.wizard'
    _description = 'Serial Number Update Wizard'

    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain=[('tracking', '!=', 'none')]  # Only allow products with tracking
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        domain="[('usage', '=', 'internal')]",
        required=True
    )
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter one serial number per line.")
    invalid_serials = fields.Text(string='Invalid/Duplicate Serials', readonly=True)

    def _get_inventory_location(self):
        """Helper method to fetch the inventory adjustment location."""
        inventory_location = self.env['stock.location'].search([('usage', '=', 'inventory')], limit=1)
        if not inventory_location:
            raise UserError(_("Inventory adjustment location not found. Please check your configuration."))
        return inventory_location

    def action_adjust_stock(self):
        """Adjust stock quantities using inventory moves."""
        if not self.scanned_serials:
            raise UserError(_("No serial numbers provided."))

        # Parse and clean serial numbers
        serial_lines = [serial.strip() for serial in self.scanned_serials.split('\n') if serial.strip()]
        if not serial_lines:
            raise UserError(_("No valid serial numbers provided."))

        # Validate product tracking
        if self.product_id.tracking == 'none':
            raise UserError(_("This wizard is only applicable for products with serial or lot tracking."))

        # Fetch the inventory adjustment location
        inventory_location = self._get_inventory_location()

        # Track seen serials, duplicates, and results
        seen_serials = set()
        duplicate_serials = []
        created_lots = []

        for serial in serial_lines:
            if serial in seen_serials:
                duplicate_serials.append(serial)
                continue
            seen_serials.add(serial)

            # Check if the lot already exists
            lot = self.env['stock.production.lot'].search([
                ('name', '=', serial),
                ('product_id', '=', self.product_id.id)
            ], limit=1)

            if lot:
                # Check if the serial number already exists in the specified location
                quant_exists = self.env['stock.quant'].search([
                    ('product_id', '=', self.product_id.id),
                    ('location_id', '=', self.location_id.id),
                    ('lot_id', '=', lot.id),
                    ('quantity', '>', 0)  # Ensure the serial number is already in stock
                ], limit=1)

                if quant_exists:
                    raise UserError(_(
                        "The serial number '%s' already exists for this product at the specified location. "
                        "Please ensure serial numbers are unique."
                    ) % serial)

            else:
                # Auto-create the lot
                lot = self.env['stock.production.lot'].create({
                    'name': serial,
                    'product_id': self.product_id.id,
                    'company_id': self.env.company.id,
                })
                created_lots.append(serial)

            # Create a stock move to adjust the stock quantity
            self._create_stock_move(lot, inventory_location)

        # Feedback message
        message = f"""
        ✅ Stock Adjustment Completed!
        ------------------------
        🔢 Total Scanned: {len(serial_lines)}
        🆕 Lots Auto-Created: {len(created_lots)}
        ♻️ Duplicates Ignored: {len(duplicate_serials)}
        📍 Location: {self.location_id.display_name}
        """

        # Return an action to close the wizard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stock Adjustment'),
                'message': message,
                'sticky': False,
                'type': 'success',
            },
        }, {
            'type': 'ir.actions.act_window_close'
        }

    def _create_stock_move(self, lot, inventory_location):
        """Create a stock move to adjust the stock quantity."""
        move_vals = {
            'name': _('Inventory Adjustment for %s' % self.product_id.name),
            'product_id': self.product_id.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
            'location_id': inventory_location.id,  # Use the inventory adjustment location
            'location_dest_id': self.location_id.id,
            'state': 'confirmed',
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'qty_done': 1,
                'location_id': inventory_location.id,
                'location_dest_id': self.location_id.id,
                'lot_id': lot.id,
            })],
        }
        move = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        move._action_done()