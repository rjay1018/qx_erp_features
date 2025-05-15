from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    entry_document_ids = fields.One2many(
        'hr.employee.document', 'employee_ref',
        domain=[('document_name.document_type', '=', 'entry')],
        string='Entry Documents'
    )

    exit_document_ids = fields.One2many(
        'hr.employee.document', 'employee_ref',
        domain=[('document_name.document_type', '=', 'exit')],
        string='Exit Documents'
    )
