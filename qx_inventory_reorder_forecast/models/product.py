from odoo import models, fields, api
from datetime import datetime, timedelta

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Average number of units sold per week, computed based on past X days of outgoing stock moves
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
    # - ok: more than Y weeks left
    # - warning: Z to Y weeks
    # - critical: less than Z weeks
    forecast_status = fields.Selection([
        ('ok', '✅ Healthy'),
        ('warning', '⚠️ Low'),
        ('critical', '🔥 Urgent')
    ], 
    string="Forecast Status", 
    compute="_compute_forecast_data", 
    store=True
    )

    def _get_config(self):
        """Retrieve configurable parameters from system settings."""
        return {
            'history_days': int(self.env['ir.config_parameter'].sudo().get_param('inventory_reorder_forecast.history_days', 90)),
            'critical_threshold': int(self.env['ir.config_parameter'].sudo().get_param('inventory_reorder_forecast.critical_threshold', 7)),
            'warning_threshold': int(self.env['ir.config_parameter'].sudo().get_param('inventory_reorder_forecast.warning_threshold', 21)),
        }

    @api.depends('qty_available')  # Trigger recomputation when stock changes
    def _compute_forecast_data(self):
        StockMove = self.env['stock.move']
        config = self._get_config()

        for product in self:
            # Handle edge case: negative stock
            if product.qty_available < 0:
                product.avg_weekly_usage = 0
                product.days_until_oos = 0
                product.forecast_status = 'critical'
                continue

            # Calculate history period start date
            date_from = fields.Datetime.to_string(datetime.now() - timedelta(days=config['history_days']))

            # Use read_group to aggregate outgoing stock moves efficiently
            outgoing_data = StockMove.read_group(
                [
                    ('product_id', '=', product.id),
                    ('state', '=', 'done'),
                    ('location_id.usage', '=', 'internal'),       # From internal location
                    ('location_dest_id.usage', '!=', 'internal'), # To external (sales/shipment)
                    ('date', '>=', date_from)
                ],
                ['product_uom_qty'],
                ['product_id']
            )
            total_out_qty = outgoing_data[0]['product_uom_qty'] if outgoing_data else 0

            # Calculate average weekly usage (e.g., 90 days = ~13 weeks)
            weeks_in_history = config['history_days'] / 7
            avg_weekly = total_out_qty / weeks_in_history if total_out_qty else 0
            product.avg_weekly_usage = avg_weekly

            # Estimate days until out of stock (based on average weekly usage)
            if avg_weekly > 0:
                product.days_until_oos = int(product.qty_available / (avg_weekly / 7))
            else:
                # If no historical usage, assume infinite time until OOS
                product.days_until_oos = 9999

            # Categorize forecast health using configurable thresholds
            if product.days_until_oos > config['warning_threshold']:
                status = 'ok'        # More than warning threshold
            elif config['critical_threshold'] < product.days_until_oos <= config['warning_threshold']:
                status = 'warning'   # Between critical and warning thresholds
            else:
                status = 'critical'  # Less than critical threshold
            product.forecast_status = status