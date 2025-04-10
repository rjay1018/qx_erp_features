from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_open_serial_scanner(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Serial Scanner',
            'res_model': 'serial.inbound.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id
            }
        }
