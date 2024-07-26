import json

from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.urls import reverse
from django.template.loader import render_to_string

from toolkit.models import TrafficLightObjects
from toolkit.my_lib import sdp_func_lib, snmpmanagement_v2

menu_header = [
        {'title': 'Главная страница', 'url_name': 'home'},
        {'title': 'О сайте', 'url_name': 'about'},
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


menu_common = [
    {'id': 1, 'title': 'Управление по SNMP', 'url_name': 'manage_snmp'},
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

controllers_menu = [
    {'id': 1, 'title': 'Swarco', 'url_name': 'swarco'},
    {'id': 3, 'title': 'Peek', 'url_name': 'peek'},
    {'id': 4, 'title': 'Поток', 'url_name': 'potok'},
]


def test_ajax(request):
    print(f'request.GET: {request.GET}')

    if request.GET:
        ip_adress = request.GET.get("ip_adress")
        protocol = request.GET.get("protocol")

        print(f'request.GET ip_adress: {ip_adress}')
        print(f'request.GET protocol: {protocol}')

    else:
        print('nnnnnooo')
        return HttpResponse('error_get_data', content_type='text/html')


    # curr_stage = snmpmanagement_v2.get_stage_stcip_potok(ip_adress)
    # print(f'ip_adress: {ip_adress}')
    # print(f'curr_stage obj1 {curr_stage}')

    if protocol == 'Swarco_STCIP':
        obj = snmpmanagement_v2.Swarco(ip_adress)
        curr_stage = obj.get_stage_stcip_swarco()
        curr_plan = obj.get_plan_stcip_swarco()
    elif protocol == 'Поток_STCIP':
        obj = snmpmanagement_v2.PotokS(ip_adress)
        curr_stage = obj.get_stage_stcip_potok()
        curr_plan = obj.get_plan_stcip_potok()
    else:
        curr_stage = curr_plan = None

    print(f'curr_stage obj {curr_stage}')
    print(f'curr_plan obj {curr_plan}')


    json_data = {
        'stage': curr_stage,
        'curr_plan': curr_plan,
    }



    return HttpResponse(json.dumps(json_data), content_type='text/html')

def set_snmp_ajax(request):

    print(f'set_snmp_ajax')
    print(f'request.GET: {request.GET}')


    if request.GET:
        ip_adress = request.GET.get("ip_adress")
        protocol = request.GET.get("protocol")

        print(f'request.GET ip_adress: {ip_adress}')
        print(f'request.GET protocol: {protocol}')

    else:
        print('nnnnnooo')
        return HttpResponse('error_get_data', content_type='text/html')

    # curr_stage = snmpmanagement_v2.get_stage_stcip_potok(ip_adress)
    # print(f'ip_adress: {ip_adress}')
    # print(f'curr_stage obj1 {curr_stage}')

    if protocol == 'Swarco_STCIP':
        pass
    elif protocol == 'Поток_STCIP':
        obj = snmpmanagement_v2.PotokS(ip_adress)
        set_req = obj.set_stage_stcip_potok('4')
    else:
        set_req = 'Косяяяк'

    print(f'set_req obj {set_req}')


    json_data = {
        'set_command': set_req,
    }

    return HttpResponse(json.dumps(json_data), content_type='text/html')

def my_python_function ( request ): # Ваш код Python здесь
    response_data = {'message' : 'Функция Python вызвана успешно!'}
    print(response_data)
    return JsonResponse(response_data)


def index(request):
    print('ind')

    data = {'title': 'Главная страница',
            'menu_header': menu_header,
            'menu2': data_db2,
            'menu_common': menu_common,
            'controllers_menu': controllers_menu,
           }
    return render(request, 'toolkit/index.html', context=data)

def about(request):
    return render(request, 'toolkit/about.html', {'title': 'О сайте', 'menu_header': menu_header})

def manage_snmp(request):

    protocols = ('UG405_Поток', 'STCIP_Поток', 'STCIP_Swarco', 'UG405_Peek')


    first_row_settings = {'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'}
    second_row_get = {'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК', 'label_data': 'Данные с ДК'}
    third_row_set = {'set_btn': 'Отправить'}

    host_data = {
        'first_row_settings': first_row_settings,
        'second_row_get': second_row_get,
        'third_row_set': third_row_set,
        'num_hosts': tuple(i for i in range(1, 10)),
        'protocols': protocols,
    }

    return render(request, 'toolkit/manage_snmp.html', context=host_data)


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
        'menu': menu_header,
        'controller': controller,
        'cat_selected': 1,

    }

    return render(request, 'toolkit/about_controller.html', context=data)


    # return HttpResponse(f'Отображение вкладки с id = {post_id}')


def calc_cyc(request):
    data = {'title': 'Расчёт циклов и сдвигов', 'menu_header': menu_header}
    return render(request, 'toolkit/calc_cyc.html', context=data)

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

    title = 'Расчёт концликтов'

    if not sdp_func_lib.check_query(query, table_name):
        # print(f'table_stages: {query.get(table_name)}')
        return render(request, 'toolkit/calc_conflicts.html', context={'render_conflicts_data': False,
                                                                       'menu_header': menu_header,
                                                                       'title': title})


    # print(f'req_GET: {query.get(table_name).strip()}')
    data_from_table_stages = query.get(table_name).split('\n')
    # print(f'req_GET: {data_from_table_stages}')

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

    sorted_stages, kolichestvo_napr, matrix_output, matrix_swarco_F997, conflict_groups_F992, \
        binary_val_swarco_for_write_PTC2, binary_val_swarco_F009 = sdp_func_lib.calculate_conflicts(
            stages=stages,
            controller_type='swarco',
            add_conflicts_and_binval_calcConflicts=True
)


    print(f'sorted_stages: {sorted_stages}')
    print(f'kolichestvo_napr: {kolichestvo_napr}')
    print(f'matrix_output: {matrix_output}')
    print(f'matrix_swarco_F997: {matrix_swarco_F997}')
    print(f'conflict_groups_F992: {conflict_groups_F992}')
    print(f'binary_val_swarco_for_write_PTC2: {binary_val_swarco_for_write_PTC2}')
    print(f'binary_val_swarco_F009: {binary_val_swarco_F009}')


    data = {
        'menu_header': menu_header,
        'title': title,
        'render_conflicts_data': True,
        'values': ('| K|', '| O|'),
        'matrix': matrix_output,
        'sorted_stages': sorted_stages,
        'kolichestvo_napr': kolichestvo_napr,
        'matrix_swarco_F997': matrix_swarco_F997,
        'conflict_groups_F992': conflict_groups_F992,
        'binary_val_swarco_F009': binary_val_swarco_F009,
    }


    return render(request, 'toolkit/calc_conflicts.html', context=data)


def controller_swarco(request):
    data = {'title': 'Swarco', 'menu_header': menu_header}
    return render(request, 'toolkit/swarco.html', context=data,)

def controller_peek(request):
    data = {'title': 'Peek', 'menu_header': menu_header}
    return render(request, 'toolkit/peek.html', context=data)

def controller_potok(request):
    data = {'title': 'Поток', 'menu_header': menu_header}
    return render(request, 'toolkit/potok.html', context=data)