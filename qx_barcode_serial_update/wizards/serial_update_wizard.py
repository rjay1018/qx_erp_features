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
        required=True
    )
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter one serial number per line.")

    def action_create_stock_quants(self):
        """Process scanned serials, validate, and create stock quants."""
        if not self.scanned_serials:
            raise UserError(_("No serial numbers provided."))

        serial_lines = self.scanned_serials.strip().split('\n')
        seen_serials = set()
        valid_lots = []
        invalid_serials = []

        for serial in serial_lines:
            serial = serial.strip()
            if not serial:
                continue

            if serial in seen_serials:
                invalid_serials.append(f"Duplicate in input: {serial}")
                continue
            seen_serials.add(serial)

            lot = self.env['stock.production.lot'].search([
                ('name', '=', serial),
                ('product_id', '=', self.product_id.id)
            ], limit=1)

            if not lot:
                invalid_serials.append(f"Not found: {serial}")
                continue

            valid_lots.append(lot)

        if not valid_lots:
            raise UserError(_("No valid serials found to create stock quants.\n\nIssues:\n%s") % '\n'.join(invalid_serials))

        # Create or update stock quants
        for lot in valid_lots:
            self.env['stock.quant']._update_available_quantity(
                product_id=self.product_id,
                location_id=self.location_id,
                quantity=1,
                lot_id=lot
            )

        message = f"""
        ✅ Stock Quants Created!
        ------------------------
        Total Scanned: {len(serial_lines)}
        Valid: {len(valid_lots)}
        Invalid: {len(invalid_serials)}
        Location: {self.location_id.display_name}
        """

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
