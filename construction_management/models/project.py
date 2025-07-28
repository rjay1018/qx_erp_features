# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    # Add fields for construction management
    critical_path = fields.Char(string='Critical Path')
    cost_sheet = fields.One2many('construction.cost.sheet', 'project_id', string='Cost Sheet')
    milestone_ids = fields.One2many('construction.milestone', 'project_id', string='Milestones')
    purchase_order_ids = fields.One2many('purchase.order', 'project_id', string='Purchase Orders')
    planning_ids = fields.One2many('construction.planning', 'project_id', string='Planning')
    document_ids = fields.One2many('construction.document', 'project_id', string='Documents')
    quality_control_ids = fields.One2many('construction.quality.control', 'project_id', string='Quality Control')

class Task(models.Model):
    _inherit = 'project.task'

    # Add fields for construction management
    task_location = fields.Char(string='Task Location')
    planning_id = fields.Many2one('construction.planning', string='Planning')

class Milestone(models.Model):
    _name = 'construction.milestone'
    _description = 'Construction Milestone'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    deadline = fields.Date(string='Deadline')
    is_completed = fields.Boolean(string='Is Completed')
    is_reached = fields.Boolean(string='Is Reached')

class CostSheet(models.Model):
    _name = 'construction.cost.sheet'
    _description = 'Construction Cost Sheet'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    budget = fields.Float(string='Budget')
    actual_cost = fields.Float(string='Actual Cost', compute='_compute_actual_cost', store=True)
    subcontractor_costs = fields.Float(string='Subcontractor Costs')
    material_costs = fields.Float(string='Material Costs')
    labor_costs = fields.Float(string='Labor Costs')

    @api.depends('project_id.timesheet_ids', 'project_id.purchase_order_ids')
    def _compute_actual_cost(self):
        for record in self:
            # Implement logic to calculate actual cost
            record.actual_cost = 0.0
