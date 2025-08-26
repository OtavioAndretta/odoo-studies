from odoo import fields, api, models
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, date



class ContractContract(models.Model):
    _name ='contract.contract'
    _description ='Gerenciador de contratos'


    name = fields.Char(string='Nome do contrato', default='Novo contrato')
    cliente = fields.Many2one('res.partner', string ='Cliente', required = True, store = True)
    start_date = fields.Date(string ='Data de início do contrato', required = True)
    end_date = fields.Date(string ='Data de fim do contrato', required = True, )
    renewal_period = fields.Integer(string='Período de renovação (dias)', default=30)
    previous_contract_id = fields.Many2one('contract.contract', string='Contrato anterior')

    currency_id = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_id, readonly=True)

    amount_total = fields.Monetary(string ='Valor do contrato',currency_field= 'currency_id', required = True)


    type_contract = fields.Selection([
        ('prestacao','Prestação de serviço'),
        ('aluguel','Aluguel'),
        ('manutencao','Manutenção')
    ])


    state = fields.Selection([
        ('draft','Rascunho'),
        ('active','Ativo'),
        ('expired','Expirado'),
        ('renewed','Renovado'),
        ('cancelled','Cancelado'),
    ], default ='draft', string ='Status do contrato')

    auto_renew = fields.Boolean(string ='Renovação automática')
    is_expired = fields.Boolean(string='Vencido', compute='_compute_expired', store=True)
    observations = fields.Text(string ='Observações ou cláusulas')
            

    @api.depends('end_date')
    def _compute_expired(self):
        today = date.today()
        for record in self:
            record.is_expired = record.end_date < today




    @api.model
    def auto_renew_contracts(self):
        hoje = date.today()
        alvo = hoje + timedelta(days = 30)
        contratos = self.search([
        ('state', '=', 'active'),
        ('auto_renew', '=', True),
        ('end_date', '<=', alvo) #busca todos que estao ativos, com auto renew ligado e que a data do fim é menor que a data de hj + 30 dias
        ])

        for contrato in contratos:
            novo = contrato.copy({
            'start_date': contrato.end_date + timedelta(days=1),
            'end_date': contrato.end_date + timedelta(days=contrato.renewal_period or 30),
            'state': 'renewed'
        })
        self.env['contract.renewal'].create({
            'contract_id': novo.id,
            'previous_contract_id': contrato.id,
            'renewal_date': hoje,
            'user_id': self.env.user.id
        })



    @api.depends('end_date','state')
    def _check_is_expired(self):
        today = date.today()
        for record in self:
            record.is_expired = record.end_date < today and record.state in ['active','renewed']

    def action_confirm(self):
        for record in self:
            if record.state != 'active':
                if not record.start_date or not record.amount_total:
                    raise UserError('Contrato precisa de data e valor')
                record.state ='active'

    
    def action_cancel(self):
        for record in self:
            if record.state != 'cancelled':
                if not record.start_date or not record.amount_total:
                    raise UserError('Contrato precisa de data e valor')
                record.state ='cancelled'

    def action_set_draft(self):
        for record in self:
            if record.state != 'draft':
                record.state = 'draft'



    def action_expire(self):
        today = date.today()
        for record in self:
            if record.end_date < today and record.state in ['active','renewed']:
                record.state = 'expired'


    @api.constrains('start_date','end_date')
    def _check_date(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError('A data final não pode ser menor que a data de início')
    


    def action_renew(self): #forma manual de renovar o contrato
        for contrato in self:
            if contrato.auto_renew and contrato.state in ['active', 'expired']:
             contrato._renew_contract()


    
    def _renew_contract(self):
        novo_contrato = self.copy({
        'start_date': self.end_date + timedelta(days=1),
        'end_date': self.end_date + timedelta(days=self.renewal_period or 30),
        'state': 'renewed',
        'previous_contract_id': self.id
    })
        self.env['contract.renewal'].create({
        'contract_id': novo_contrato.id,
        'previous_contract_id': self.id,
        'renewal_date': date.today(),
        'user_id': self.env.user.id
    })




