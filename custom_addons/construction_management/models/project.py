# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    # Add fields for construction management
    critical_path = fields.Char(string='Critical Path')
    cost_sheet = fields.One2many('construction.cost.sheet', 'project_id', string='Cost Sheet')
    milestone_ids = fields.One2many('construction.milestone', 'project_id', string='Milestones')

class Task(models.Model):
    _inherit = 'project.task'

    # Add fields for construction management
    task_location = fields.Char(string='Task Location')

class Milestone(models.Model):
    _name = 'construction.milestone'
    _description = 'Construction Milestone'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    deadline = fields.Date(string='Deadline')
    is_completed = fields.Boolean(string='Is Completed')

class CostSheet(models.Model):
    _name = 'construction.cost.sheet'
    _description = 'Construction Cost Sheet'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    budget = fields.Float(string='Budget')
    actual_cost = fields.Float(string='Actual Cost', compute='_compute_actual_cost', store=True)

    @api.depends('project_id.timesheet_ids', 'project_id.purchase_order_ids')
    def _compute_actual_cost(self):
        for record in self:
            # Implement logic to calculate actual cost
            record.actual_cost = 0.0
