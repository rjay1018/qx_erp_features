from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class EmployeeChecklistDocumentWizard(models.TransientModel):
    _name = 'employee.checklist.document.wizard'
    _description = 'Checklist Document Upload Wizard'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    checklist_item_id = fields.Many2one(
        'employee.checklist',
        string='Checklist Item',
        required=True,
        domain="[('document_type', 'in', ['entry', 'exit'])]",
    )
    attachment = fields.Binary(string="Document File", required=True)
    attachment_filename = fields.Char("Filename")
    description = fields.Text("Description")

    def action_upload(self):
        if not self.attachment:
            raise ValidationError(_("Please upload a document."))

        # Create the attachment first
        attachment = self.env['ir.attachment'].create({
            'name': self.attachment_filename or self.checklist_item_id.name,
            'datas': self.attachment,
            'res_model': 'hr.employee.document',
        })

        # Create the employee document
        self.env['hr.employee.document'].create({
            'name': self.attachment_filename or f'Doc-{self.checklist_item_id.name}',
            'employee_ref': self.employee_id.id,
            'doc_attachment_id': [(6, 0, [attachment.id])],
            'document_name': self.checklist_item_id.id,
            'description': self.description or self.checklist_item_id.name,
        })
