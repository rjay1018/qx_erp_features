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

    def action_create_stock_quants(self):
        """Process scanned serials, auto-create lots if needed, and create stock quants."""
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
        valid_lots = []
        created_lots = []

        # Batch search for existing lots
        existing_lots = self.env['stock.production.lot'].search([
            ('name', 'in', serial_lines),
            ('product_id', '=', self.product_id.id)
        ])
        existing_lot_names = {lot.name: lot for lot in existing_lots}

        # Process each serial number
        for serial in serial_lines:
            if serial in seen_serials:
                duplicate_serials.append(serial)
                continue
            seen_serials.add(serial)

            # Check if the lot already exists
            if serial in existing_lot_names:
                valid_lots.append(existing_lot_names[serial])
            else:
                # Create a new lot
                new_lot = self.env['stock.production.lot'].create({
                    'name': serial,
                    'product_id': self.product_id.id,
                    'company_id': self.env.company.id,
                })
                valid_lots.append(new_lot)
                created_lots.append(serial)

        if not valid_lots:
            raise UserError(_("No serial numbers could be processed."))

        # Ensure inventory mode is enabled
        self = self.with_context(inventory_mode=True)

        # Create or update stock quants
        for lot in valid_lots:
            self.env['stock.quant']._update_available_quantity(
                product_id=self.product_id,
                location_id=self.location_id,
                quantity=1,
                lot_id=lot
            )

        # Save invalids to display if needed
        self.invalid_serials = '\n'.join(duplicate_serials)

        # Build feedback message
        message = f"""
        ✅ Stock Quants Created!
        ------------------------
        🔢 Total Scanned: {len(serial_lines)}
        🆕 Lots Auto-Created: {len(created_lots)}
        ♻️ Duplicates Ignored: {len(duplicate_serials)}
        📍 Location: {self.location_id.display_name}
        """

        if created_lots:
            message += f"\n\n🆕 Created Lots:\n{', '.join(created_lots)}"
        if duplicate_serials:
            message += f"\n\n♻️ Duplicate Serials:\n{', '.join(duplicate_serials)}"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Stock Update'),
                'message': message,
                'sticky': False,
                'type': 'success',
            }
        }