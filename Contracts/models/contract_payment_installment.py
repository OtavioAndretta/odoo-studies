from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime, date

class ContractPaymentInstallment(models.Model):
    _name ='contract.payment.installment'
    _description ='Gerenciar parcela específica'

    name = fields.Char(string ='Nome do contrato', compute = '_compute_name', store = True)
    contract_id = fields.Many2one('contract.contract')
    payment_id = fields.Many2one('contract.payment', string ='Plano de pagamento')

    installment_number = fields.Integer(string ='Número da parcela', compute='_compute_installment_number')

    due_date = fields.Date(string ='Data de vencimento da parcela', compute ='_compute_due_date')

    amount_installment = fields.Monetary(string ='Valor da parcela', currency_field='contract_id.currency_id', store = True)

    paid = fields.Boolean(string ='Pago', store = True)
    payment_date = fields.Date(string ='Data de pagamento', compute = '_compute_payment_date', store = True)

    payment_method = fields.Selection(related ='payment_id.payment_method', store = True)

    state = fields.Selection([
        ('open','Em aberto'),
        ('paid','Pago'),
        ('late','Atrasado'),
        ('cancelled','Cancelado'),
    ], default = 'open', string ='Status da parcela')

    is_late = fields.Boolean(string ='Atrasado', compute ='_compute_islate')
    days_late = fields.Integer(compute='_compute_days_late', string='Dias atrasado', store=True)

    note = fields.Text(string ='Notas')

    @api.depends('payment_id','payment_id.installment_ids')
    def _compute_installment_number(self):
        for record in self:
            if record.payment_id:
                total = record.payment_id.installment_ids.sorted(key = lambda r: r.id) #ordena pelo id das parcelas
                for idx, parcela in enumerate(total, start =1): #Esse trecho percorre todas as parcelas ordenadas e compara cada uma com a parcela atual (record). Quando encontra a parcela correspondente, atribui o índice (idx) como número da parcela. O break encerra o loop assim que encontra a parcela certa.
                    if parcela.id == record.id:
                        record.installment_number = idx
                        break
            else: #ainda acho confuso o que acontece, porem, nada dalem da conta, uma forma de filtrar as parcelas
                record.installment_number = 0


    @api.depends('installment_number', 'contract_id.start_date', 'payment_id.installment_ids.due_date')
    def _compute_due_date(self):
        for record in self:
            if not record.contract_id or not record.installment_number:
                record.due_date = False
                continue
            if record.installment_number == 1:
                record.due_date = record.contract_id.start_date + timedelta(days = 30)
            
            else:
                anteriores = record.payment_id.installment_ids.filtered(lambda r: r.installment_number and r.installment_number < record.installment_number).sorted(key=lambda r: r.installment_number) #Isso significa: “pegue todas as parcelas anteriores à atual”. no filtered
                #filtra as parcelas e ordena elas

                if anteriores:
                    ultima = anteriores[-1]
                    record.due_date = ultima.due_date + timedelta(days = 30)
                else:
                    record.due_date = record.contract_id.start_date + timedelta(days = 30)

    @api.depends('state')
    def _compute_payment_date(self):
            for record in self:
                if record.state and record.state =='paid':
                    record.payment_date = date.today()

        
    @api.depends('paid', 'due_date')
    def _compute_state(self):
        today = date.today()
        for record in self:
            if record.paid:
                record.state = 'paid'
            elif record.due_date and record.due_date < today:
                record.state = 'late'
            else:
                record.state = 'open'

    @api.depends('due_date', 'paid')
    def _compute_islate(self):
        today = date.today()
        for record in self:
            if record.due_date and record.due_date < today and not record.paid:
                record.is_late = True
            else:
                record.is_late = False

    @api.depends('due_date', 'paid')
    def _compute_days_late(self):
        today = date.today()
        for record in self:
            if record.due_date and record.due_date < today and not record.paid:
                record.days_late = (today - record.due_date).days
            else:
                record.days_late = 0



    @api.depends('contract_id.name')
    def _compute_name(self):
        for record in self:
            record.name = record.contract_id.name if record.contract_id else f"Contrato de {record.id}"