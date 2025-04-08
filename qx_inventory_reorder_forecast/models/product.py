from odoo import models, fields, api
from datetime import datetime, timedelta

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Average number of units sold per week, computed based on past 90 days of outgoing stock moves
    avg_weekly_usage = fields.Float(
        string="Avg Weekly Usage", 
        compute="_compute_forecast_data", 
        store=True
    )

    # Estimated number of days remaining before the product runs out of stock
    days_until_oos = fields.Integer(
        string="Est. Days Until Out of Stock", 
        compute="_compute_forecast_data", 
        store=True
    )

    # Visual indicator for stock health based on forecast:
    # - ok: more than 3 weeks left
    # - warning: 1 to 3 weeks
    # - critical: less than 1 week
    forecast_status = fields.Selection([
        ('ok', '✅ Healthy'),
        ('warning', '⚠️ Low'),
        ('critical', '🔥 Urgent')
    ], 
    string="Forecast Status", 
    compute="_compute_forecast_data", 
    store=True
    )

    @api.depends('qty_available')  # Trigger recomputation when stock changes
    def _compute_forecast_data(self):
        StockMove = self.env['stock.move']
        for product in self:
            # Calculate 90 days ago from today
            date_from = fields.Datetime.to_string(datetime.now() - timedelta(days=90))

            # Get all completed outgoing moves for the product in the last 90 days
            outgoing_moves = StockMove.search([
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),       # from internal location
                ('location_dest_id.usage', '!=', 'internal'), # to external (sales/shipment)
                ('date', '>=', date_from)
            ])

            # Total quantity moved out
            total_out_qty = sum(move.product_uom_qty for move in outgoing_moves)

            # Calculate average weekly usage (13 weeks = ~90 days)
            avg_weekly = total_out_qty / 13 if total_out_qty else 0
            product.avg_weekly_usage = avg_weekly

            # Estimate days until out of stock (based on average weekly usage)
            product.days_until_oos = int(product.qty_available / (avg_weekly / 7)) if avg_weekly else 9999

            # Categorize forecast health
            if product.days_until_oos > 21:
                status = 'ok'        # 3+ weeks buffer
            elif 7 < product.days_until_oos <= 21:
                status = 'warning'   # 1–3 weeks left
            else:
                status = 'critical'  # Less than 1 week
            product.forecast_status = status
