from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SerialUpdateWizard(models.TransientModel):
    _name = 'serial.update.wizard'
    _description = 'Serial Number Update Wizard'
    _inherit = ["barcodes.barcode_events_mixin"]  # Add barcode event mixin

    product_id = fields.Many2one('product.product', string='Product', required=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        domain="[('usage', '=', 'internal')]",
        required=True,
        help="Select the stock location where the serials will be stored."
    )
    scanned_serials = fields.Text(string='Scanned Serials', help="Enter serial numbers separated by new lines.")
    lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Valid Serials',
        compute='_compute_lot_ids',
        store=False  # Do not persist this relationship in the database
    )
    invalid_serials = fields.Text(string='Invalid/Duplicate Serials', readonly=True)

    @api.depends('scanned_serials')
    def _compute_lot_ids(self):
        """Compute the list of valid lots based on scanned serials."""
        for wizard in self:
            if wizard.scanned_serials:
                serial_lines = wizard.scanned_serials.split('\n')
                valid_lots = []

                for serial in serial_lines:
                    serial = serial.strip()
                    if serial:
                        lot = self.env['stock.production.lot'].search([
                            ('name', '=', serial),
                            ('product_id', '=', wizard.product_id.id)
                        ], limit=1)
                        if lot:
                            valid_lots.append(lot.id)

                wizard.lot_ids = [(6, 0, valid_lots)]
            else:
                wizard.lot_ids = False

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

                valid_lots.append(lot.id)

            # Update invalid serials
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

    def on_barcode_scanned(self, barcode):
        """
        Handle barcode scanning for serial numbers.
        This method processes the scanned barcode and updates the wizard's state.
        """
        # Validate that the product and location are set
        if not self.product_id or not self.location_id:
            raise UserError(_("Please select a product and stock location before scanning."))

        # Check if the scanned barcode is already in the list of valid serials
        if barcode in [lot.name for lot in self.lot_ids]:
            raise UserError(_("Duplicate serial number detected: %s") % barcode)

        # Validate the barcode against existing stock.production.lot records
        lot = self.env['stock.production.lot'].search([
            ('name', '=', barcode),
            ('product_id', '=', self.product_id.id)
        ], limit=1)

        if not lot:
            # Append invalid serials
            invalid_serials = self.invalid_serials.split('\n') if self.invalid_serials else []
            invalid_serials.append(barcode)
            self.invalid_serials = '\n'.join(invalid_serials)
            raise UserError(_("Invalid serial number detected: %s") % barcode)

        # Add the valid serial to the list of scanned serials
        scanned_serials = self.scanned_serials.split('\n') if self.scanned_serials else []
        scanned_serials.append(barcode)
        self.scanned_serials = '\n'.join(scanned_serials)

        # Create a stock quant for the scanned serial
        self._create_stock_quant([lot.id])

        # Notify the user
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Serial number %s has been added successfully.') % barcode,
                'sticky': False,
            }
        }