from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ContractsPayment(models.Model):
    _name ='contract.payment'
    _description ='Pagamento de contratos'
    name = fields.Char(string ='Nome do contrato', compute = '_compute_name', store = True)
    contract_id = fields.Many2one('contract.contract', string ='Contrato', required = True)

    #depois colocar due date apenas de exibicao, amount total e status, alem da data de pagamento, apenas como exibicao, quem ira controlar isto sera o contract_payment_installment

    start_date = fields.Date(related = 'contract_id.start_date', string ='Data de início', store = True)
    end_date = fields.Date(related ='contract_id.end_date', string ='Data de término', store = True)
    observation = fields.Text(related ='contract_id.observations', string ='Obserações/Cláusulas', store = True)

    #modo que foi pago, isto irá gerar uma due_date, um booleano paid, payment_date
    payment_mode = fields.Selection([
        ('unique','Pagamento Único'),
        ('installmental','Parcelado'),
        ('scheduled','Pagamento Agendado')
    ], default ='unique', string ='Modo de pagamento', store = True)

    installment_number = fields.Integer(string ='Número de Parcelas', store = True)
    installment_ids = fields.One2many('contract.payment.installment', 'payment_id', string='Parcelas')
    payment_method = fields.Selection([
        ('pix','Pix'),
        ('boleto','Boleto'),
        ('card','Cartão')
    ], default = None, string ='Métodos de pagamento')



    @api.constrains('payment_mode', 'contract_id')
    def _check_payment_mode_consistency(self):
        for record in self:
            if record.payment_mode != record.contract_id.payment_mode:
                raise ValidationError('O modo de pagamento do contrato não pode ser alterado. Escolheu parcelado, vai parcelado.')


    @api.constrains('payment_mode')
    def _check_payment_mode(self):
        for record in self:
            if record.contract_id.state == 'active':
                raise ValidationError('Não é possível alterar o modo de pagamento após ativação do contrato.')


    @api.constrains('installment_number')
    def _check_installment_number(self):
        for record in self:
            if record.payment_mode =='unique' and record.installment_number not in(0,1):
                raise ValidationError('Erro, pagamento único deve ser de apenas uma parcela')
            elif record.payment_mode =='installmental':
                if record.installment_number <= 0 or record.installment_number > 40:
                    raise ValidationError('Erro: As parcelas devem ser entre 1 e 40')
            elif record.payment_mode == 'scheduled' and record.installment_number not in (0, 1):
                    raise ValidationError('Pagamento agendado deve ter no máximo uma parcela.')
            
   
 


    @api.depends('contract_id.name')
    def _compute_name(self):
        for record in self:
            record.name = record.contract_id.name if record.contract_id else f"Contrato de {record.id}"













