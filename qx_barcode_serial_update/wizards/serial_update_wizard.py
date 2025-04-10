# -*- coding: utf-8 -*-
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

            if not lot:
                # Auto-create the lot
                lot = self.env['stock.production.lot'].create({
                    'name': serial,
                    'product_id': self.product_id.id,
                    'company_id': self.env.company.id,
                })
                created_lots.append(serial)

            # Create a stock move to adjust the stock quantity
            self._create_stock_move(lot)

        # Feedback message
        message = f"""
        ✅ Stock Adjustment Completed!
        ------------------------
        🔢 Total Scanned: {len(serial_lines)}
        🆕 Lots Auto-Created: {len(created_lots)}
        ♻️ Duplicates Ignored: {len(duplicate_serials)}
        📍 Location: {self.location_id.display_name}
        """

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stock Adjustment'),
                'message': message,
                'sticky': False,
                'type': 'success',
            }
        }

    inventory_location = self.env['stock.location'].search([('usage', '=', 'inventory')], limit=1)
    if not inventory_location:
        raise UserError(_("Inventory adjustment location not found. Please check your configuration."))

    move_vals = {
        'name': _('Inventory Adjustment for %s' % self.product_id.name),
        'product_id': self.product_id.id,
        'product_uom_qty': 1,
        'product_uom': self.product_id.uom_id.id,
        'location_id': inventory_location.id,  # Use the dynamically found location
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