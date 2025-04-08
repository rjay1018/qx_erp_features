from odoo import models, fields, api
from datetime import datetime, timedelta

class ProductProduct(models.Model):
    _inherit = 'product.product'

    avg_weekly_usage = fields.Float(string="Avg Weekly Usage", compute="_compute_forecast_data", store=True)
    days_until_oos = fields.Integer(string="Est. Days Until Out of Stock", compute="_compute_forecast_data", store=True)
    forecast_status = fields.Selection([
        ('ok', '✅ Healthy'),
        ('warning', '⚠️ Low'),
        ('critical', '🔥 Urgent')
    ], string="Forecast Status", compute="_compute_forecast_data", store=True)

    @api.depends('qty_available')
    def _compute_forecast_data(self):
        StockMove = self.env['stock.move']
        for product in self:
            # Get moves for last 90 days (outgoing)
            date_from = fields.Datetime.to_string(datetime.now() - timedelta(days=90))
            outgoing_moves = StockMove.search([
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '!=', 'internal'),
                ('date', '>=', date_from)
            ])
            total_out_qty = sum(move.product_uom_qty for move in outgoing_moves)
            avg_weekly = total_out_qty / 13 if total_out_qty else 0

            product.avg_weekly_usage = avg_weekly
            product.days_until_oos = int(product.qty_available / (avg_weekly / 7)) if avg_weekly else 9999

            # Set status
            if product.days_until_oos > 21:
                status = 'ok'
            elif 7 < product.days_until_oos <= 21:
                status = 'warning'
            else:
                status = 'critical'
            product.forecast_status = status
