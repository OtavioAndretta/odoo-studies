from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class SubscriptionCustumer(models.Model):
    #nome e descricao
    _name ='subscription.costumer'
    _description ='Vinculo de clientes ao plano'
    
    #info de cliente

    partner_id =fields.Many2one('res.partner', string ='Usuário', required = True)
    email_partner = fields.Char(related='partner_id.email', store=True)
    phone = fields.Char(related='partner_id.phone', store=True)

    # info do plano

    plan_id = fields.Many2one('subscription.plan',string ='Plano Assinado', required = True) #se relaciona com os planos criados no subscription_plan
    start_date = fields.Date(string ='Data de início do plano', required = True)
    duration = fields.Integer(string='Duração personalizada', required=False)
    end_date = fields.Date(string ='Data de término do plano', compute ='_compute_end_date')
    #atividade do plano

    is_active =fields.Boolean(string ='Ativo', default = True)
    auto_renew = fields.Boolean(string='Renovação automática', default = True)

    #cobranças e pagamentos

    last_payment_date = fields.Date(string ='Data pagamento anterior', required = True)
    next_due_date = fields.Date(string ='Próximo pagamento', compute ='_compute_next_due_date')
    payment_status = fields.Selection([
        ('paid','Pago'),
        ('pending','Em andamento'),
        ('failed','Pagamento falhou')
    ], default = 'pending', string='Status do pagamento')

    payment_method = fields.Selection([
        ('boleto','Boleto'),
        ('card','Cartão'),
        ('pix','Pix')
    ], default =False, string ='Método de pagamento')

    #validacoes no banco

    _sql_constraints =[
        ('UniqueEmail','unique(email_partner)','Email já cadastrado'),
        ('UniquePhone','unique(phone)','Telefone já cadastrado')
    ]



    @api.depends('start_date','duration')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.duration:
                record.end_date = record.start_date + timedelta(days = record.duration)
            else:
                record.end_date = False

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.plan_id and record.duration > record.plan_id.duration:
                raise ValidationError ('A duração da assinatura não pode exceder a duração do plano')
            
    @api.depends('last_payment_date','plan_id.billing_cycle')
    def _compute_next_due_date(self):
        for record in self:
            if record.last_payment_date and record.plan_id.billing_cycle:
                cycle = record.plan_id.billing_cycle
                if cycle =='monthly':
                    record.next_due_date = record.last_payment_date + timedelta(days = 30)
                elif cycle =='quarterly':
                    record.next_due_date = record.last_payment_date + timedelta(days = 90)
                elif cycle =='yearly':
                    record.next_due_date = record.last_payment_date + timedelta(days = 365)
                else:
                    record.next_due_date = False
            
    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id:
            self.duration = self.plan_id.duration



    @api.constrains('start_date','end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("A data de término não pode ser anterior à data de início.")
            
    
    @api.constrains('plan_id')
    def _check_plan_capacity(self):
        for record in self:
            if record.plan_id.assinaturas_remanescentes <= 0:
                raise ValidationError(f'Sem vagas para o plano {record.plan_id.plano}')

      




