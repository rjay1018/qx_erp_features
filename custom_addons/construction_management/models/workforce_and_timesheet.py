# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    project_ids = fields.Many2many('project.project', string='Projects')

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _compute_overtime(self):
        for line in self:
            # Implement logic to calculate overtime
            line.overtime = 0.0

    overtime = fields.Float(string='Overtime', compute='_compute_overtime')
