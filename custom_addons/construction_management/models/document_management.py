# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Document(models.Model):
    _inherit = 'documents.document'

    project_id = fields.Many2one('project.project', string='Project')

class Drawing(models.Model):
    _name = 'construction.drawing'
    _description = 'Construction Drawing'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    attachment = fields.Binary(string='Attachment', required=True)
    version = fields.Char(string='Version')
