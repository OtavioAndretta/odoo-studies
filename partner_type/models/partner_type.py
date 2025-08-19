from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ClientType(models.Model):
    _inherit ='res.partner'
    
    customer_type =fields.Selection([
        ('regular','Cliente Regular'),
        ('vip','Cliente VIP'),
        ('prospect','Prospect')
        
    ], string='Tipo de cliente', default ='regular')