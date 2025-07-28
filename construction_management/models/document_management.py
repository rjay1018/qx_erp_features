# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ConstructionDocument(models.Model):
    _name = 'construction.document'
    _description = 'Construction Document'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    attachment = fields.Binary(string='Attachment', required=True)
    version = fields.Char(string='Version')
    description = fields.Text(string='Description')
    date_uploaded = fields.Date(string='Date Uploaded', default=fields.Date.context_today)
    uploaded_by = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user)
