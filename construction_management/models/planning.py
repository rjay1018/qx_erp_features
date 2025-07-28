# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ConstructionPlanning(models.Model):
    _name = 'construction.planning'
    _description = 'Construction Planning'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    duration = fields.Float(string='Duration', compute='_compute_duration', store=True)
    task_ids = fields.One2many('project.task', 'planning_id', string='Tasks')

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration = (record.end_date - record.start_date).days
            else:
                record.duration = 0.0
