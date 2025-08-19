from odoo import models, fields, api

class TestePagamentos(models.Model):
    _name ="meu_teste.pagamento"
    _description = "Teste de pagamento"
    
    name = fields.Char(string='Nome do Pagamento') #label que aparece na interface do Odoo.
    state = fields.Selection([
        ('draft','Rascunho'),
        ('posted','Publicado'),
        ('cancel','Cancelado') 
        
    ], default = 'draft') #odo novo registro começa como "Rascunho". esse campo é usado para controlar o estado do pagamento, semelhante a workflow.


    partner_id = fields.Many2one('res.partner', string ='Cliente') #funciona como uma chave estrangeira: cada pagamento pode ter apenas um cliente associado.