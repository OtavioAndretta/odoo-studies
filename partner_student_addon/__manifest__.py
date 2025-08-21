{
    "name": "Partner Student Addon",
    "version": "1.0",
    "summary": "Adiciona campos de curso, data de inicio, duração e fim.",
    "description": "Adiciona partners como estudantes, cria possibilidade de registrar um curso e atribuir pessoas a ele, alem de definir a duração e as vagas para o curso(updates futuro irão adicionar local e outras funções).",
    "author": "Otávio Andretta",
    "category": "Training",
    "depends": ["base","contacts"],
    "data": [
        'security/ir.model.access.csv',
        'views/partner_student.xml',
    ],
    "installable": True,
    "application": True,
}