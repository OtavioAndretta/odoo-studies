from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date


class CourseRegistration(models.Model):
    _name = 'course.registration'
    _description = 'Course registration'

    course_id = fields.Many2one('course.course', string='Curso')
    student_id = fields.Many2one('res.partner', string='Estudante')
    registration_date = fields.Date(default=fields.Date.today, string='Data de registro do curso')
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado')
    ], default='draft', string='Status do aluno')

    #ações botoes
    def action_confirm(self):
        for record in self:
            if record.course_id.seats_left > 0:
                record.state = 'confirmed'
            else:
                raise ValidationError("Sem vagas disponíveis no curso")

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_cancelled(self):
        for record in self:
            record.state = 'cancelled'

    #validando
    @api.constrains('state')
    def _check_seats(self):
        for record in self:
            if record.state == 'confirmed':
                confirmed_count = len(record.course_id.students_ids.filtered(lambda r: r.state == 'confirmed'))
                if confirmed_count > record.course_id.seats:
                    raise ValidationError('Não há mais vagas disponíveis neste curso')

    @api.constrains('student_id', 'course_id')
    def _check_student_duplicity(self):
        for record in self:
            existing = self.search([
                ('student_id', '=', record.student_id.id),
                ('course_id', '=', record.course_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError("O aluno já está inscrito neste curso")


class CourseStudents(models.Model):
    _name = 'course.course'
    _description = 'Course Model'

    start_date = fields.Date("Data de início")
    duration = fields.Integer(string='Duração em dias')
    end_date = fields.Date("Data de término", compute='_compute_end_date')
    seats = fields.Integer(string="Vagas disponíveis")

    days_left = fields.Integer(string='Dias restantes de curso', compute='_compute_days_left_course', store=True)
    seats_left = fields.Integer(string='Vagas restantes', compute='_compute_seats_left', store=True)

    active = fields.Boolean(string='Curso ativo', default=True)
    students_ids = fields.One2many('course.registration', 'course_id', string='Inscritos')

    
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for record in self:
            if record.start_date and record.duration:
                record.end_date = record.start_date + timedelta(days=record.duration)
            else:
                record.end_date = False

    @api.depends('end_date')
    def _compute_days_left_course(self):
        for record in self:
            if record.end_date:
                delta = record.end_date - date.today()
                record.days_left = max(delta.days, 0)
            else:
                record.days_left = 0

    @api.depends('seats', 'students_ids.state')
    def _compute_seats_left(self):
        for record in self:
            if record.seats and record.students_ids:
                confirmed_students = len(record.students_ids.filtered(lambda r: r.state == 'confirmed'))
                record.seats_left = max(record.seats - confirmed_students, 0)
            else:
                record.seats_left = 0
