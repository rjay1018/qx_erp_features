from odoo import models, fields, _ 

class EmployeeChecklist(models.Model):
    _inherit = 'employee.checklist'

    description = fields.Text(string='Description')
    
    def action_upload_document_from_checklist(self):
        employee_id = self.env.context.get('default_employee_id')
        if not employee_id:
            raise UserError("No employee in context.")

        return {
            'type': 'ir.actions.act_window',
            'name': _('Upload Document'),
            'res_model': 'employee.checklist.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': employee_id,
                'default_checklist_item_id': self.id,
            }
        }
