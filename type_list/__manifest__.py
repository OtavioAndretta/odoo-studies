{
    'name':'Clientes premium',
    'version':'1.0',
    'summary':'Módulo com propósito de adicionar opções de clientes VIPS ou regulares',
    'description':'Módulo com funcionalidade de adicionar clientes como VIPS e listar sua data de início, e automaticamente calcular a data de fim(30 dias padrão)',
    'depends':['base'],
    'data': [
        'views/res_partner_addon.xml'
    ],
    'author':"Otávio Andretta",
    'category':"Clients",


    'installable':True
}