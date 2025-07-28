# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_subcontractor = fields.Boolean(string='Is Subcontractor')
    certification = fields.Char(string='Certification')
    compliance_info = fields.Text(string='Compliance Info')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    retention_amount = fields.Float(string='Retention Amount')
