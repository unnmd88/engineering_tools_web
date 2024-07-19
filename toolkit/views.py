from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string



menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Возможности', 'url_name': 'options'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
        {'title': 'Вход', 'url_name': 'login'},
       ]

data_db = [
    {'id': 1, 'title': 'Управление по SNMP', 'is_published': True},
    {'id': 2, 'title': 'Фильтр SNMP', 'is_published': True},
    {'id': 3, 'title': 'Расчет цикла и сдвигов', 'is_published': True},
    {'id': 4, 'title': 'Расчет конфликтов', 'is_published': True},
]

data_db2 = ['Управление по SNMP', 'Фильтр SNMP',
            'Расчет цикла и сдвигов', 'Расчет конфликтов'
]

def index(request):

    data = {'title': 'Главная страница',
            'menu': menu,
            'menu2': data_db2,
            'posts': data_db
           }
    return render(request, 'toolkit/index.html', context=data)

def about(request):
    return render(request, 'toolkit/about.html', {'title': 'О сайте', 'menu': menu})

def manage_snmp(request):
    data = {'title': 'Управление по SNMP',
            'menu': menu,
            'menu2': data_db2,
            'posts': data_db
           }
    return render(request, 'toolkit/manage_snmp.html', context=data)


def contact(request):
    return HttpResponse('Обратная связь')

def login(request):
    return HttpResponse('Авторизация')

def options(request):
    return HttpResponse('Возможности')

def show_tab(request, post_id):
    print('1')
    return HttpResponse(f'Отображение вкладки с id = {post_id}')



# def tabs(request, tabs_id):
#     return HttpResponse(f'<h1> Странца приложения tabs </h1><p>id: {tabs_id}</p>')
#
#
# def tabs_by_slug(request, tabs_slug):
#     print(request.GET)
#     return HttpResponse(f'<h1> Странца приложения tabs </h1><p>slug: {tabs_slug}</p>')
#
# def main_page(request):
#     return HttpResponse('Главная страница')
#
#
# def archive(request, year):
#     if year > 2024:
#         uri = reverse('tabs_slug', args=('test', ))
#         return HttpResponseRedirect('/')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> Страница не найдена </h1>")