{
    'name': 'Employee Checklist Document Wizard',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Upload checklist documents for employee entry/exit processes',
    'author': 'jaynatz', 
    'depends': ['hr','oh_employee_check_list'],
    'data': [
        'views/hr_employee_form_inherit.xml',
        'wizards/employee_checklist_document_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
