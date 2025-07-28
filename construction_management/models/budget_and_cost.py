# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    def _compute_actual_vs_forecast(self):
        for project in self:
            # Implement logic to calculate actual vs forecast
            project.actual_vs_forecast = 0.0

    actual_vs_forecast = fields.Float(string='Actual vs. Forecast', compute='_compute_actual_vs_forecast')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Project')
