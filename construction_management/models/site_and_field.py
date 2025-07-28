# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DailyLog(models.Model):
    _name = 'construction.daily.log'
    _description = 'Construction Daily Log'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    work_diary = fields.Text(string='Work Diary')
    photos = fields.Many2many('ir.attachment', string='Photos')

class RFI(models.Model):
    _name = 'construction.rfi'
    _description = 'Request for Information'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', default='draft')
    question = fields.Text(string='Question')
    answer = fields.Text(string='Answer')

    def action_open(self):
        self.write({'state': 'open'})

    def action_close(self):
        self.write({'state': 'closed'})
