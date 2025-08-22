{
    'name':'Biblioteca Addon',
    'summary':'Adiciona menu de gerenciamento para bibliotecas',
    'description':'Adicionado opcao de cadastrar livros, datas e mais. Além disso, e possivel atribuir clientes a livros emprestados e adicionar quantidades de livros, IDS e codigo ISBN(codigo unico)',
    'author':'Otávio Andretta',
    'category':'books',
    'depends':['base','contacts'],
    'data':[
        'security/ir.model.access.csv',
        'views/library_addon.xml',
        'views/library_loan.xml',
    ],


    'installable':True,
    'application':True


}