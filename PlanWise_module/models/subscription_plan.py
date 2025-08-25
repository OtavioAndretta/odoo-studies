from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date



class SubscriptionPlan(models.Model):
    #init do modulo
    _name ='subscription.plan'
    _description ='Definir planos e preços'
 # detalhes do plano
    name = fields.Char(string='Nome do Plano', related='plano', store=True)
    plano = fields.Char(string ='Nome do plano', required = True)
    code = fields.Char(string ='Código do plano', required = True)
    description = fields.Char(string='Descrição')

    #Precificação agora

    price = fields.Monetary(string ='Preço', required = True, currency_field ='currency_id')
    currency_id = fields.Many2one('res.currency', string ='Moeda')

    billing_cycle = fields.Selection([
        ('monthly','Mensal'),
        ('quarterly','Trimestralmente'),
        ('yearly','Anualmente'),
    ], default ='monthly', string='Ciclo de Cobrança', store = True)

    trial_days = fields.Integer(string ='Dias de teste gratuito', required = True, default = 7)

    #duracao e renovacao automatica computada com api.depends

    available_from = fields.Date(string='Data de início do plano', required = True)
    duration =fields.Integer(string='Duração em dias', required = True)
    end_date = fields.Date(string='Data final', compute = '_compute_remaining_days')
    auto_renew = fields.Boolean(string='Renovação automática', default = True)

    product_id = fields.Many2one('product.product', string='Produto Vinculado')
    payment_provider = fields.Selection([
        ('stripe','Stripe'),
        ('mercado_pago','Mercado Pago'),
    ], default ='stripe', string ='Provedor de pagamento')

    assinaturas = fields.Integer(string='Quantidade de assinaturas', required = True)
    assinaturas_remanescentes = fields.Integer(string ='Assinaturas restantes', compute ='_compute_remaining_subscriptions')

    #ativo ou nao

    is_active = fields.Boolean(string='Plano ativo', default = True)

    _sql_constraints = [
        ('planID_unique','unique(code)', 'O código do plano deve ser único para cada plano')
    ]



    @api.depends('available_from','duration')
    def _compute_remaining_days(self):
        for record in self:
            if record.available_from and record.duration:
               record.end_date = record.available_from+ timedelta(days = record.duration)
            else:
                record.end_date = False

    #apenas validações para ter certeza e deixar bonito o módulo
    @api.constrains('price','duration','trial_days')
    def _check_values(self):
        for record in self:
            if record.price <0:
                raise ValidationError('Preço tem que ser maior que 0')
            if record.duration < 0:
                raise ValidationError('A duração do plano deve ser maior que 0 dias')
            if record.trial_days < 0:
                raise ValidationError('O numero de dias teste deve ser 0 ou maior')
            
            
    @api.depends('assinaturas')
    def _compute_remaining_subscriptions(self):
        for record in self:
            total_assinantes = self.env['subscription.costumer'].search_count([('plan_id','=', record.id), ('is_active', '=', True)]) # esse método vai pegar todos os costumer, e usar o metodo search_count, e comparar se o id do plano é o mesmo salvo com eles, se for e constar que o plano ta ativo, então eles são contados como assinantes daquele determinado plano, self.env bem util, começar a usar mais.
            record.assinaturas_remanescentes = record.assinaturas - total_assinantes

# segundo o gpt, se houver muitas querys, muitos clientes, pode sobrecarregar o banco, entao seria mais eficiente pensar em mudar para um read_group ou algo do tipo, mas por enquanto vou manter assim