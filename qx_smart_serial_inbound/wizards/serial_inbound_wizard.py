from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SerialInboundWizard(models.TransientModel):
    _name = 'serial.inbound.wizard'
    _description = 'Serial Inbound Scanner Wizard'

    picking_id = fields.Many2one('stock.picking', required=True)
    last_scanned = fields.Char("Last Scanned Serial")
    scanned_serials = fields.Text("Scanned Serials", readonly=True)

    @api.onchange('last_scanned')
    def _onchange_last_scanned(self):
        if not self.last_scanned:
            return

        serial = self.last_scanned.strip()
        move_line = self.env['stock.move.line'].search([
            ('picking_id', '=', self.picking_id.id),
            ('lot_name', '=', False),
            ('product_id.tracking', '=', 'serial'),
            ('qty_done', '=', 0),
        ], limit=1)

        if not move_line:
            raise ValidationError(f"No open serial slot available for: {serial}")

        move_line.write({
            'lot_name': serial,
            'qty_done': 1,
        })

        existing = self.scanned_serials or ""
        self.scanned_serials = f"{existing}\n{serial}".strip()
        self.last_scanned = ''
