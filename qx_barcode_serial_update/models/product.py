from odoo import models, fields, api 
 
class ProductProduct(models.Model): 
    _inherit = 'product.product' 
 
    def open_serial_inbound_update_wizard(self): 
        """Open the wizard for serial number inbound update.""" 
        return { 
            'name': 'Serial/Lot Inbound Update', 
            'type': 'ir.actions.act_window', 
            'res_model': 'serial.update.wizard', 
            'view_mode': 'form', 
            'target': 'new', 
            'context': {'default_product_id': self.id}, 
        } 
