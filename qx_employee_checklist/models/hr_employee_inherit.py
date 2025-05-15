from odoo import models

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    def action_open_checklist_upload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Checklist Document Upload',
            'res_model': 'employee.checklist.document.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            }
        }
