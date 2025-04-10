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
    valid_lot_ids = fields.Many2many('stock.production.lot', string='Valid Lots', readonly=True)
    invalid_serials = fields.Text(string='Invalid/Duplicate Serials', readonly=True)

    @api.onchange('scanned_serials')
    def _onchange_scanned_serials(self):
        """Process scanned serials and validate them."""
        if not self.scanned_serials:
            self.valid_lot_ids = [(5, 0, 0)]  # Clear any previous records
            self.invalid_serials = False
            return

        serial_lines = self.scanned_serials.split('\n')
        valid_lots = []
        invalid_serials = []
        seen_serials = set()

        for serial in serial_lines:
            serial = serial.strip()
            if not serial:
                continue

            # Check for duplicates within input
            if serial in seen_serials:
                invalid_serials.append(f"Duplicate in input: {serial}")
                continue
            seen_serials.add(serial)

            # Validate serial number
            lot = self.env['stock.production.lot'].search([
                ('name', '=', serial),
                ('product_id', '=', self.product_id.id)
            ], limit=1)

            if not lot:
                invalid_serials.append(f"Not found: {serial}")
                continue

            valid_lots.append(lot.id)

        # Store valid and invalid results
        self.valid_lot_ids = [(6, 0, valid_lots)]
        self.invalid_serials = '\n'.join(invalid_serials) if invalid_serials else False

    def action_create_stock_quants(self):
        """Create stock quant records for valid serials at the selected location."""
        lots = self.valid_lot_ids

        if not lots:
            raise UserError(_("No valid serials found to create stock quants."))

        for lot in lots:
            # Create or update stock.quant for each serial
            self.env['stock.quant']._update_available_quantity(
                product_id=self.product_id,
                location_id=self.location_id,
                quantity=1,
                lot_id=lot
            )

        # Build success message
        message = f"""
        ✅ Stock Quant Creation Successful:
        ------------------------------------
        ✅ Total Serials Scanned: {len(self.scanned_serials.splitlines())}
        ✅ Valid Serials Processed: {len(lots)}
        📍 Stock Location: {self.location_id.display_name}
        """

        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Stock Quants'),
            'res_model': 'stock.quant',
            'view_mode': 'tree,form',
            'domain': [('lot_id', 'in', lots.ids), ('location_id', '=', self.location_id.id)],
            'target': 'current',
            'context': dict(self.env.context, default_location_id=self.location_id.id),
        }
