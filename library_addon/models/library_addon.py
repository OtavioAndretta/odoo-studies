from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Date
from datetime import timedelta, date


class LibraryBook(models.Model):
    _name ='library.book'
    _description = 'Addon for Library Management'

    name = fields.Char(string='Nome do livro', required=True)
    author = fields.Char(string='Autor do livro', required=True)

    codigo_isbn = fields.Char(string='Código ISBN do livro', required=True)

    total_copies = fields.Integer(string='Cópias', default=1)
    available_copies = fields.Integer(string='Cópias disponíveis', compute='_compute_available_copies', store=True) #store=True faz com que o campo seja armazenado no banco de dados, e não apenas calculado em tempo real

    active = fields.Boolean(string="Ativo", default=True)

    cover_image = fields.Binary(string='Capa do Livro') #campo binario para armazenar a imagem da capa do livro


    emprestimo_ids = fields.One2many('library.loan','book_id',string='Empréstimos') #one 2 many é usado aqui pois um livro pode ter varios emprestimos, como se tivesse indo de um para muitos, o primeiro campo é o nome do modelo de emprestimo, e o segundo se liga ao id do livro

    _sql_constraints = [
    ('isbn_unique', 'unique(codigo_isbn)', 'O código ISBN deve ser único.')
]

    @api.depends('emprestimo_ids.state','total_copies')
    def _compute_available_copies(self):
        for record in self:
            emprestado = len(record.emprestimo_ids.filtered(lambda r:r.state in ['borrowed','requested'])) #ele vai percorrer todos os emprestimos daquele livro e contar quantos estao com o estado 'borrowed'
            record.available_copies = max(record.total_copies - emprestado, 0) #isso evita ter livros negativos.
     

class LibraryLoan(models.Model):
    _name='library.loan'
    _description='Registro de Empréstimo de Livros'

    book_id = fields.Many2one('library.book',string='Livro', required=True) #many2one é usado aqui pois um emprestimo so pode ter um livro, o primeiro campo é o nome do modelo de livro, e o segundo é o nome do campo que vai aparecer na tela

    partner_id =fields.Many2one('res.partner', string='Usuário', required = True) #o primeiro campo é o nome do modelo de parceiro, e o segundo é o nome do campo que vai aparecer na tela

    emprestimo_date = fields.Date(string='Data de Empréstimo', default = fields.Date.context_today, required = True)
    dias_emprestimo = fields.Integer(string ='Duração do Empréstimo (dias)', default=7, required = True)
    return_date = fields.Date(string='Data de Devolução', compute = '_compute_return_date', store = True)

    state = fields.Selection([
        ('requested','Solicitado'),
        ('draft', 'Rascunho'),
        ('borrowed', 'Emprestado'),
        ('returned', 'Devolvido'),
        ('overdue', 'Atrasado')
    ], default='draft', string='Status do Empréstimo')

    @api.depends('emprestimo_date', 'dias_emprestimo')
    def _compute_return_date(self):
        for record in self:
            if record.emprestimo_date:
                record.return_date = record.emprestimo_date + timedelta(days = record.dias_emprestimo) # o timedelta faz o calculo de tempo misturando datas e dias 
            else:
                record.return_date = False
    def action_borrow(self):
        for record in self:
            if record.book_id.available_copies > 0:
                record.state = 'borrowed'
            else:
                raise ValidationError("Não há cópias disponíveis para empréstimo deste livro.")
            
    def action_return(self):
        for record in self:
            if record.state == 'borrowed':
                record.state = 'returned'
            else:
                raise ValidationError("Este livro não está emprestado.")
            
    def action_overdue(self):
        for record in self:
            if record.state == 'borrowed' and record.return_date < date.today():
                record.state = 'overdue'
            else:
                raise ValidationError("Este livro não está atrasado.")
            
    def action_renew(self, extra_days=7):
       for record in self:
           if record.state == 'borrowed':
               record.dias_emprestimo += extra_days
               record._compute_return_date() #projeto futuro de noticicar o usuario via email ou whatsapp acerca do atraso do livro

    @api.constrains('partner_id','book_id') #aqui vai ser uma validação pra evitar que alguem pegue livro estando com um ja emprestado
    def _check_duplicate_loan(self):
        for record in self:
            if record.state =='borrowed':
                duplicate = self.search([
                    ('book_id','=', record.book_id.id), #procura registros onde o livro de emprestimo seja o mesmo do atua
                    ('partner_id','=', record.partner_id.id), #dcheca os registros em que o usuario seja o mesmo do atual
                    ('state','=','borrowed'),
                    ('id','!=', record.id)
                ])
                if duplicate:
                    raise ValidationError(
                    "O usuário %s já possui um empréstimo ativo para o livro %s." % (record.partner_id.name, record.book_id.name)
                )#garante que so ocorre o erro se houver emprestimo ativo, se nao, ele lanca o true que é o que o constrains espera para validar a regra

