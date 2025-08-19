from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

 
class RePartner(models.Model):
    _inherit ='res.partner'
    
    birth_date = fields.Date(string="Data de Aniversário")
    
@api.constrains('birth_date') #decorador usado para definir validações de regras em campos específicos, neste caso ele acessa o birth_date para fazer isto
def _check_birth_date(self):
    for rec in self: #garante funcionalidade do self caso ele contenha 1 ou N registros pois o self pode no odoo pode armazenar mais de um registro ao mesmo tempo
        if rec.birth_date and rec.birth_date > date.today(): #aqui vai criar um if se a data existir e foi inserida e se é maior que o dia de hoje
            raise ValidationError("A data de aniversãrio não pode ser no futuro")