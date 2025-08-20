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
    #dias restantes pra acabar o vip
    days_left =fields.Integer(string='Dias restantes do VIP:', compute ='_compute_days_left') #ele é integer pois representa um numero de dias restantes
    #quando estiver faltando 7 dias, vai soltar um aviso no odoo, e por isto, ele é boolean
    vip_alert = fields.Boolean(string="Dias restantes", compute ="_compute_days_left")

    @api.depends('start_date','customer_type')
    def _compute_end_date(self):
        for record in self:
            if record.customer_type =='vip' and record.start_date:
                record.end_date = record.start_date + timedelta(days = 30)
            else:
                record.end_date = False

    @api.depends('end_date','customer_type')
    def _compute_days_left(self):
        for record in self:
            if record.customer_type =='vip' and record.end_date:
                record.days_left = (record.end_date - fields.Date.today()).days #data de hj em dias
                record.vip_alert = record.days_left <= 5
            else:
                record.days_left = 0
                record.vip_alert = False

    @api.onchange('customer_type') #isto aqui irá executar quando o usuário mudar o valor no formulário!
    def _onchange_customer_type(self):
        if self.customer_type =='vip':
           self.start_date = Date.context_today(self)
        else:
            self.start_date = False

    @api.constrains('start_date','customer_type')
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
