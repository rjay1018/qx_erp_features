from odoo import models

class HrEmployeeDocument(models.Model):
    _inherit = 'hr.employee.document'

    def action_open_upload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Document',
            'res_model': 'employee.checklist.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.employee_ref.id,
                'default_checklist_item_id': self.document_name.id,
            }
        }
