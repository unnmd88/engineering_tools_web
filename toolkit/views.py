from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.urls import reverse
from django.template.loader import render_to_string

from toolkit.models import TrafficLightObjects
from toolkit.my_lib import sdp_func_lib, django_lib

menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Возможности', 'url_name': 'options'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
        {'title': 'Вход', 'url_name': 'login'},
       ]

# data_db = [
#     {'id': 1, 'title': 'Управление по SNMP', 'is_published': True},
#     {'id': 2, 'title': 'Фильтр SNMP', 'is_published': True},
#     {'id': 3, 'title': 'Расчет цикла и сдвигов', 'is_published': True},
#     {'id': 4, 'title': 'Расчет конфликтов', 'is_published': True},
# ]


data_db = [
    {'id': 1, 'title': 'Управление по SNMP', 'url_name': 'manage_snmp'},
    {'id': 2, 'title': 'Фильтр SNMP', 'url_name': 'filter_snmp'},
    {'id': 3, 'title': 'Расчет цикла и сдвигов', 'url_name': 'calc_cyc'},
    {'id': 4, 'title': 'Расчет конфликтов', 'url_name': 'calc_conflicts'},
]

data_db2 = ['Управление по SNMP', 'Фильтр SNMP',
            'Расчет цикла и сдвигов', 'Расчет конфликтов'
]

# controller_types_db = [
#     {'id': 1, 'name': 'Swarco'},
#     {'id': 2, 'name': 'Peek'},
#     {'id': 3, 'name': 'Поток S'},
#     {'id': 4, 'name': 'Поток'}
# ]

controller_types_db = ['Swarco', 'Peek', 'Поток S', 'Поток']


def index(request):

    data = {'title': 'Главная страница',
            'menu': menu,
            'menu2': data_db2,
            'posts': data_db,
            'controllers': controller_types_db,
           }
    return render(request, 'toolkit/index.html', context=data)

def about(request):
    return render(request, 'toolkit/about.html', {'title': 'О сайте', 'menu': menu})

def manage_snmp(request):

    return render(request, 'toolkit/manage_snmp.html',)


def contact(request):
    return HttpResponse('Обратная связь')

def login(request):
    return HttpResponse('Авторизация')

def options(request):
    return HttpResponse('Возможности')

def show_tab(request, post_id):
    print('1')
    controller = get_object_or_404(TrafficLightObjects, pk=post_id)


    data = {
        'num_CO': controller.ip_adress,
        'menu': menu,
        'controller': controller,
        'cat_selected': 1,

    }

    return render(request, 'toolkit/about_controller.html', context=data)


    # return HttpResponse(f'Отображение вкладки с id = {post_id}')


def calc_cyc(request):
    print('calc_cyc')
    return HttpResponse(request, 'toolkit/calc_cyc.html')

def calc_conflicts(request):
    print('calc_conflicts')
    data = {'title': 'Расчёт конфликтов', 'menu': menu}
    return render(request, 'toolkit/calc_conflicts.html', context=data)



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

def data_for_calc_conflicts(request):

    table_name = 'table_stages'
    query = request.GET

    if not sdp_func_lib.check_query(query, table_name):
        print(f'table_stages: {query.get(table_name)}')
        return render(request, 'toolkit/calc_conflicts.html', context={'render_conflicts_data': False})



    print(f'req_GET: {query.get(table_name).strip()}')
    data_from_table_stages = query.get(table_name).split('\n')
    print(f'req_GET: {data_from_table_stages}')

    stages = []
    for num, line in enumerate(data_from_table_stages):
        if ':' in line:
            processed_line = line.replace("\r", '').split(':')[1]
        else:
            processed_line = line.replace("\r", '')

        processed_line = processed_line.split(',')

        print(f'processed_line: {processed_line}')
        stages.append(processed_line)


    print(data_from_table_stages)
    print(stages)

    sorted_stages, kolichestvo_napr, matrix_output, matrix_swarco_F997, binary_val_swarco_for_write_PTC2, \
        binary_val_swarco_F009 = sdp_func_lib.calculate_conflicts(
            stages=stages,
            controller_type='swarco',
            add_conflicts_and_binval_calcConflicts=True
)


    print(f'sorted_stages: {sorted_stages}')
    print(f'kolichestvo_napr: {kolichestvo_napr}')
    print(f'matrix_output: {matrix_output}')
    print(f'matrix_swarco_F997: {matrix_swarco_F997}')
    print(f'binary_val_swarco_for_write_PTC2: {binary_val_swarco_for_write_PTC2}')
    print(f'binary_val_swarco_F009: {binary_val_swarco_F009}')




#     result = sdp_func_lib.calculate_conflicts(
#             stages=stages,
# )

    data = {
        'title': 'Расчёт концликтов',
        'render_conflicts_data': True,
        'values': ('| K|', '| O|'),
        'matrix': matrix_output,
        'sorted_stages': sorted_stages,
        'kolichestvo_napr': kolichestvo_napr,
        'matrix_swarco_F997': matrix_swarco_F997


    }


    return render(request, 'toolkit/calc_conflicts.html', context=data)
