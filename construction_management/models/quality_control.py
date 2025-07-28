# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ConstructionQualityControl(models.Model):
    _name = 'construction.quality.control'
    _description = 'Construction Quality Control'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    task_id = fields.Many2one('project.task', string='Task')
    inspection_date = fields.Date(string='Inspection Date', default=fields.Date.context_today)
    inspected_by = fields.Many2one('res.users', string='Inspected By', default=lambda self: self.env.user)
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Status', default='fail')
    notes = fields.Text(string='Notes')
