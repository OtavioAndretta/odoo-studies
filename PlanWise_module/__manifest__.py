{
    'name':'Subscriptia',
    'summary':'Módulo que cria planos e gerencia faturas e clientes',
    'description':'criação de planos, atribuição de clientes, automatizações e envio de faturas(futuramente por email e PDF)',
    'author':'Otávio Andretta',
    'version':'1.0',
    'depends':['base','contacts'],
    'category':'Subscriptions',
    'data':[
        'security/ir.model.access.csv',
        'views/subscription_plan_view.xml',
        'views/subscription_costumer_view.xml',
        'views/subscription_invoice_view.xml',
    ],



    'installable': True,
    'application': True

}