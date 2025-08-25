from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class SubscriptionInvoice(models.Model):
    #criação
    _name = 'subscription.invoice'
    _description ='Gerador de faturas e afins'

    #relacionando com o cliente o modulo agora
    customer_id = fields.Many2one('subscription.costumer', string='Cliente', required=True)
    plan_id = fields.Many2one('subscription.plan', string='Plano', required=True)
    currency_id = fields.Many2one('res.currency', string='Moeda', default=lambda self: self.env.company.currency_id)
    partner_id = fields.Many2one(related ='customer_id.partner_id', string ='Usuário') #um campo derivado, que te dá acesso direto ao res.partner, útil pra exibir nome, email, endereço, etc., sem duplicar dados.]


    #datas importantes
    emission_date = fields.Date(string='Data de emissão', required = True)
    expire_date = fields.Date(string ='Data de vencimento', default = lambda self: date.today() + timedelta(days = 7)) #default de 7 dias
    payment_date = fields.Date(string ='Data de pagamento', compute ='_compute_payment_date')
    covered_invoice_time = fields.Date(string ='Período coberto de uso pela fatura',default = lambda self: date.today() + timedelta(days =30)) #default 30 dias

    #dados financeiros
    price = fields.Monetary(related ='plan_id.price', string ='Preço', store = True)
    discount_percent = fields.Float(string ='Desconto(%)')
    price_with_discount = fields.Monetary(string='Preço com disconto', currency_field='currency_id', compute ='_compute_discount')


    #status fatura
    state = fields.Selection([
        ('draft','Rascunho'),
        ('sent','Enviada'),
        ('paid','Paga'),
        ('overdue','Atrasada'),
        ('cancelled','Cancelada'),

    ], default = 'draft', string ='Status da fatura'
    )
    payment_method = fields.Selection(related = 'customer_id.payment_method', string ='Método de pagamento', store = True) #como eu ja criei isso no subscription.costumer, aqui só referencio para a fatura ser gerada.

    #conteudo da fatura
    description_invoice = fields.Text(string ='Descriçao')
    plan_code_for_invoice = fields.Char(related ='plan_id.code', store = True)
    invoice_number = fields.Char(string ='Número da fatura', required = True)


    _sql_constraints = [
        ('unique_invoiceNumber','unique(invoice_number)','Cada fatura tem um número único'),
        ('positive_price','CHECK(price>=0)','O preço da fatura tem que ser maior que 0')
    ]

    @api.depends('price','discount_percent')
    def _compute_discount(self):
        for record in self:
            if record.price and record.discount_percent:
                record.price_with_discount = record.price - (record.price * record.discount_percent/100)
            else:
                record.price_with_discount = record.price or 0.0
    #checando disconto

    @api.constrains('discount_percent')
    def _check_discount_percent(self):
        for record in self:
            if not 0 <= record.discount_percent <= 100:
                raise ValidationError('O desconto deve estar entre 0 e 100%')
    #validacao 50% automatica, porem no futuro quando eu tiver mais conhecimento, vou tentar integrar com alguma api, tipo stripe ou mercado pago, ou pagSeguro.

    @api.depends('state')
    def _compute_payment_date(self):
        for record in self:
            if record.state =='paid' and not record.payment_date:
                record.payment_date = date.today()
            elif record.state != 'paid':
                record.payment_date = False

    @api.constrains('expire_date')
    def _check_expire_date(self):
        for record in self:
            if record.expire_date < record.emission_date:
                raise ValidationError('A data de expiramento não pode ser antes da data de emissão')



    def action_generate_invoice(self):
       for record in self:
           if not record.plan_id or not record.partner_id:
               raise ValidationError("Plano e cliente devem estar preenchidos para gerar a fatura.")

           record.emission_date = date.today()
           record.expire_date = date.today() + timedelta(days=7)
           record.covered_invoice_time = date.today() + timedelta(days=30)
           record.state = 'sent'

           if not record.invoice_number:
               record.invoice_number = f"INV-{record.id or 'TEMP'}"

           record.description_invoice = f"Fatura do plano {record.plan_id.name} para {record.partner_id.name}"

    


    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.plan_id = self.customer_id.plan_id

    

    def name_get(self):
        result = []
        for record in self:
           partner_name = record.partner_id.name or "Cliente desconhecido"
           invoice_number = record.invoice_number or "Sem número"
           state_label = dict(self._fields['state'].selection).get(record.state, "Desconhecido")
           name = f"{partner_name} - {invoice_number} [{state_label}]"
           result.append((record.id, name))
        return result
