from odoo import models, fields, api

class EmployeeChecklistDocumentWizard(models.TransientModel):
    _name = 'employee.checklist.document.wizard'
    _description = 'Checklist Document Upload Wizard'

    employee_id = fields.Many2one('hr.employee', required=True)
    checklist_item_id = fields.Many2one('employee.checklist', required=True)
    attachment = fields.Binary(string="Attachment", required=True)
    attachment_filename = fields.Char()
    description = fields.Text()

    def action_upload(self):
        self.env['hr.employee.document'].create({
            'employee_ref': self.employee_id.id,
            'document_name': self.checklist_item_id.id,
            'description': self.description,
            'doc_attachment_id': [(0, 0, {
                'name': self.attachment_filename,
                'datas': self.attachment,
                'res_model': 'hr.employee',
                'res_id': self.employee_id.id,
            })],
        })
        return {'type': 'ir.actions.act_window_close'}
