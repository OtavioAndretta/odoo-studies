from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import timedelta, date

class ContractContract(models.Model):
    _name = 'contract.contract'
    _description = 'Gerenciador de contratos'

    name = fields.Char(string='Nome do contrato', compute ='_compute_name', store = True)
    cliente = fields.Many2one('res.partner', string='Cliente', required=True, store=True)

    installment_ids = fields.One2many('contract.payment.installment', 'contract_id', string='Parcelas') #se liga ao .py que gerencia parcelas especificas, e ao id do contrato

    start_date = fields.Date(string='Data de início do contrato', required=True)
    end_date = fields.Date(string='Data de fim do contrato', required=True)
    payment_id = fields.Many2one('contract.payment') #cria a relacao para a due date funcionar de fato

    due_date = fields.Date(related='payment_id.due_date', store=True, string ='Vencimento da parcela')
    renewal_period = fields.Integer(string='Período de renovação (dias)', default=30)

    previous_contract_id = fields.Many2one('contract.contract', string='Contrato anterior')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    amount_total = fields.Monetary(string='Valor do contrato', currency_field='currency_id', required=True)

    type_contract = fields.Selection([('prestacao', 'Prestação de serviço'), ('aluguel', 'Aluguel'), ('manutencao', 'Manutenção')])

    installment_ids = fields.One2many('contract.payment.installment', 'contract_id', string='Parcelas')

    state = fields.Selection([('draft', 'Rascunho'), ('active', 'Ativo'), ('expired', 'Expirado'), ('renewed', 'Renovado'), ('cancelled', 'Cancelado')], 
    default='draft', string='Status do contrato')

    auto_renew = fields.Boolean(string='Renovação automática')
    is_expired = fields.Boolean(string='Vencido', compute='_compute_expired', store=True)

    renewal_ids = fields.One2many(
    "contract.renewal",
    "contract_id",
    string="Histórico de renovações"
)

    
    observations = fields.Text(string='Observações ou cláusulas')

    @api.depends('end_date', 'state')
    def _compute_expired(self):
        today = date.today()
        for record in self:
            record.is_expired = record.end_date < today and record.state in ['active', 'renewed']

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError('A data final não pode ser menor que a data de início')

    @api.constrains('cliente', 'start_date', 'end_date')
    def _check_duplicate_contract(self):
        for record in self:
            contrato_existe = self.search([('id', '!=', record.id), ('cliente', '=', record.cliente.id), ('start_date', '<=', record.end_date), ('end_date', '>=', record.start_date)], limit=1)
            if contrato_existe:
                raise ValidationError('Já existe um contrato ativo para este cliente neste período.')


    #@api.model
    #def auto_renew_contracts(self):
     #   hoje = date.today()
      #  alvo = hoje + timedelta(days=30)
       # contratos = self.search([('state', '=', 'active'), ('auto_renew', '=', True), ('end_date', '<=', alvo)])
        #for contrato in contratos:
         #   novo = contrato.copy({'start_date': contrato.end_date + timedelta(days=1), 'end_date': contrato.end_date + timedelta(days=contrato.renewal_period or 30), 'state': 'renewed', 'previous_contract_id': contrato.id})
          #  self.env['contract.renewal'].create({'new_contract_id': novo.id, 'previous_contract_id': contrato.id, 'renewal_date': hoje, 'user_id': self.env.user.id})
          

    def action_confirm(self):
        for record in self:
            if record.state != 'active':
                record.state = 'active'

    def action_cancel(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'cancelled'

    def action_set_draft(self):
        for record in self:
            if record.state != 'draft':
                record.state = 'draft'

    def action_expire(self):
        today = date.today()
        for record in self:
            if record.end_date < today and record.state in ['active', 'renewed']:
                record.state = 'expired'

    def action_renew(self):
        for contrato in self:
            if contrato.state in ['active', 'expired']:
                contrato._renew_contract()

    def _renew_contract(self):
        novo_contrato = self.copy({'start_date': self.end_date + timedelta(days=1), 'end_date': self.end_date + timedelta(days=self.renewal_period or 30), 'state': 'renewed', 'previous_contract_id': self.id})
        self.env['contract.renewal'].create({'contract_id': novo_contrato.id, 'previous_contract_id': self.id, 'renewal_date': date.today(), 'user_id': self.env.user.id})


    @api.depends('cliente')
    def _compute_name(self):
        for record in self:
            record.name = f"Contrato de {record.cliente.name}" if record.cliente else f"Contrato {record.id}"

