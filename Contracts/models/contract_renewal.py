from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class ContractsRenewal(models.Model):
    _name ='contract.renewal'
    _description ='Renovação de contratos'

    name = fields.Char(string ='Nome do contrato', compute = '_compute_name', store = True)
    
    new_contract_id = fields.Many2one('contract.contract', string ='Novo contrato', required = True, ondelete ='cascade') #se deletar um contrato, todas as renovações também são deletadas

    previous_contract_id = fields.Many2one('contract.contract', string ='Contrato anterior' ,ondelete ='set null') #se deletar o contrato anterior, somente ficará vazio o campo, e nao deletará.

    renewal_date = fields.Date('Data de renovação', required = True)
    user_id = fields.Many2one('res.users', string ='Usuário responsável', default = lambda self: self.env.user, required = True) #self.env.user → retorna o usuário atual da sessão (quem está usando o Odoo, ou seja, retorna quem que renovou o contrato.

    
    @api.depends('contract_id.name')
    def _compute_name(self):
        for record in self:
            record.name = record.contract_id.name if record.contract_id else f"Contrato de {record.id}"
