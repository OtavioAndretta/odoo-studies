from odoo import models, fields, api
from odoo.fields import Date
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TypeList(models.Model):
    _inherit ='res.partner'

    customer_type =fields.Selection([
    ('regular','Cliente regular'),
    ('vip','Cliente VIP'),
    ('prospect','Cliente Prospect')    
    ],string='Tipo de cliente', default = 'regular' )

    start_date = fields.Date(string="Data de início")
    end_date = fields.Date(string='Data do fim', compute ="_compute_end_date")

    @api.depends('start_date','customer_type')
    def _compute_end_date(self):
        for record in self:
            if record.customer_type =='vip' and record.start_date:
                record.end_date = record.start_date + timedelta(days = 30)
            else:
                record.end_date = False

    @api.onchange('customer_type') #isto aqui irá executar quando o usuário mudar o valor no formulário!
    def _onchange_customer_type(self):
        if self.customer_type =='vip':
           self.start_date = Date.context_today(self)
        else:
            self.start_date = False

    @api.constrains('start_date','ecustomer_type')
    def _check_vip_dates(self):
        for record in self:
            if record.customer_type =='vip' and not record.start_date:
                raise ValidationError("Clientes VIP devem ter data de ínicio")
            if record.customer_type !='vip' and record.start_date:
                raise ValidationError("Sometente clientes VIP podem conter data de início, e consequentemente data de fim")
            
    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date > date.today():
                raise ValidationError("Impossível salvar data de início maior que o dia atual.")
