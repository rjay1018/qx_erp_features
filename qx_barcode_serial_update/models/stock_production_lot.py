from odoo import models, fields

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    # Add a Many2one field to link back to the wizard
    wizard_id = fields.Many2one('serial.update.wizard', string='Wizard Reference')