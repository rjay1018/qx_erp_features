# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _name = 'construction.purchase.request'
    _description = 'Construction Purchase Request'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    task_id = fields.Many2one('project.task', string='Task')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

class StockLocation(models.Model):
    _inherit = 'stock.location'

    project_id = fields.Many2one('project.project', string='Project')
