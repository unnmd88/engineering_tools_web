import json
import os
from datetime import datetime as dt
from io import StringIO, BytesIO

from pathlib import Path

from django.core.files import File
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.urls import reverse
from django.template.loader import render_to_string

from toolkit.forms_app import CreateConflictForm
from toolkit.models import TrafficLightObjects, UploadFiles2, SaveConflictsTXT
from toolkit.my_lib import sdp_func_lib, snmpmanagement_v2, conflicts



def reverse_slashes(path):
    path = path.replace('\\', '/')
    return path

def make_id(filename: str) -> int:
        """
        Возвращает id для модели UploadFiles2:
        swarco: 1
        peek: 2
        остальные файлы: 3
        :param filename: имя файла из коллекции request.FILEES:
        :return id_for_db -> номер группы(принадлежности)
        """
        if filename[-4:] == 'PTC2':
            id_for_db = 1
        elif filename[-3:] == 'DAT':
            id_for_db = 2
        else:
            id_for_db = 3
        return id_for_db



class ProcessedRequestBase:
    @staticmethod
    def reverse_slashes(path):
        path = path.replace('\\', '/')
        return path


class ProcessedRequestConflicts(ProcessedRequestBase):

    upload_name_id = 'upload_config_file'
    name_textarea = 'table_stages'
    controller_type = 'controller_type'

    @staticmethod
    def make_id(filename: str) -> int:
        """
        Возвращает id для модели UploadFiles2:
        swarco: 1
        peek: 2
        остальные файлы: 3
        :param filename: имя файла из коллекции request.FILEES:
        :return id_for_db -> номер группы(принадлежности)
        """
        if filename[-4:] == 'PTC2':
            id_for_db = 1
        elif filename[-3:] == 'DAT':
            id_for_db = 2
        else:
            id_for_db = 3
        return id_for_db

    @staticmethod
    def make_txt_conflicts(path_to_txt_conflicts_tmp=f'сalculated_conflicts {dt.now().strftime("%d %b %Y %H_%M_%S")}.txt'):
        with open(path_to_txt_conflicts_tmp, 'wb') as file_from_post_req:
            pass
        with open(path_to_txt_conflicts_tmp, 'rb') as fw:
            f = SaveConflictsTXT(status_file='tesT', file=path_to_txt_conflicts_tmp)
            f.file.save(path_to_txt_conflicts_tmp, File(fw))
        try:
            os.remove(path_to_txt_conflicts_tmp)
        except FileNotFoundError:
            pass

    @staticmethod
    def correct_path(path):
        return ProcessedRequestBase.reverse_slashes(path).split('media/')[1]


    def __init__(self, request):
        self.request = request
        self.post_req_dict = request.POST.dict()
        self.files_dict = request.FILES.dict()
        self.controller_type = \
            self.post_req_dict.get(self.controller_type).lower() if self.controller_type in self.post_req_dict else None
        self.val_txt_conflicts = True if 'create_txt' in self.post_req_dict else False
        self.val_add_conflicts_and_binval_calcConflicts = True if 'binval_swarco' in self.post_req_dict else False
        self.val_make_config = True if 'make_config' in self.post_req_dict else False
        self.stages = self.post_req_dict.get(self.name_textarea)

        print('-' * 25)
        print(f'self..files_dict: {self.files_dict}')
        print(f'self..val_make_config: {self.val_make_config}')



        if request.FILES:
            if 'make_config' in self.post_req_dict:
                self.val_make_config = True
            if self.upload_name_id in self.files_dict:
                self.file_from_request = self.files_dict.get(self.upload_name_id)
                print(f'self.file_from_requestT: {self.file_from_request}')
                print(f'self.file_from_requestT: {type(self.file_from_request)}')
                print('--&&---')


                self.filename_from_request = self.file_from_request.name
                print(f'request.FILES.get(upload_name_id): {request.FILES.get(self.upload_name_id)}')
                print(f'request.FILES.get(upload_name_id): {type(request.FILES.get(self.upload_name_id))}')

                print(f'request.FILES2: {request.FILES}')
                print(f'self..file_from_request: {self.file_from_request}')
                print(f'self..filename_from_request: {self.filename_from_request}')
            self.id_group = self.make_id(filename=self.filename_from_request)
        else:
            self.val_make_config = False
            self.file_from_request = False
            self.filename_from_request = False


        if self.val_txt_conflicts:
            self.make_txt_conflicts()
            self.path_to_txt_conflicts = SaveConflictsTXT.objects.last().file.path
        else:
            self.path_to_txt_conflicts = None




menu_header = [
    {'title': 'Главная страница', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
    {'title': 'Возможности', 'url_name': 'options'},
    {'title': 'Обратная связь', 'url_name': 'contact'},
    {'title': 'Вход', 'url_name': 'login'},
]

protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')

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


path_tmp = 'toolkit/tmp/'
path_uploads = 'toolkit/uploads/'


def get_snmp_ajax(request, num_host):
    print(f'request.GET: {request.GET}')

    if request.GET:
        ip_adress = request.GET.get("ip_adress")
        protocol = request.GET.get("protocol")
        scn = request.GET.get("scn")

        print(f'request.GET ip_adress: {ip_adress}')
        print(f'request.GET protocol: {protocol}')
        print(f'request.GET scn {scn}')

    else:
        print('nnnnnooo')
        return HttpResponse(json.dumps('Error: Failed to get data'), content_type='text/html')

    if len(ip_adress) < 10 or protocol not in protocols:
        return HttpResponse(json.dumps('Error: Failed to get data'), content_type='text/html')



    host = make_obj_snmp(protocol, ip_adress, scn)

    json_data = host.make_json_to_front(host)

    print(f'json_data: {json_data}')
    # if protocol == protocols[0]:
    #     json_data = {
    #         'Фаза': host.get_stage(),
    #         'План': host.get_plan(),
    #     }
    #
    # elif protocol == protocols[1]:
    #
    #     json_data = {
    #         'Фаза': host.get_stage(),
    #         'План': host.get_plan(),
    #         'Режим': host.statusMode.get(host.get_mode())
    #     }
    #
    # elif protocol == protocols[2]:
    #     json_data = {
    #         'Фаза': host.get_stage(),
    #         'План': host.get_plan(),
    #     }
    # else:
    #     json_data = {
    #         'Error': 'Сбой получения данных'
    #     }

    return HttpResponse(json.dumps(json_data, ensure_ascii=False), content_type='text/html')


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


def my_python_function(request):  # Ваш код Python здесь
    response_data = {'message': 'Функция Python вызвана успешно!'}
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
    first_row_settings = {'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'}
    second_row_get = {'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК',
                      'label_data': 'Данные с ДК'}
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

def upload_file(file):
    with open(f'{path_tmp}{file.name}', 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> Страница не найдена </h1>")


def data_for_calc_conflicts(request):
    title = 'Расчёт конфликтов'
    upload_name_id = 'upload_config_file'
    name_textarea = 'table_stages'
    query_post = request.POST

    if request.GET:
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}

        return render(request, 'toolkit/calc_conflicts.html', context=data)

    # obj = ProcessedRequestConflicts(request)




    elif request.POST:
        req_data = ProcessedRequestConflicts(request)
        UploadFiles2.objects.create(file=req_data.file_from_request, group=req_data.id_group, status_file='source')
        path_to_config_file = UploadFiles2.objects.last().file.path



        path_to_txt_conflicts = SaveConflictsTXT.objects.last().file.path

        # print('-' * 25)
        # print(f'objj.files_dict: {objj.files_dict}')
        # print(f'objj.val_make_config: {objj.val_make_config}')
        # print(f'objj.file_from_request: {objj.file_from_request}')
        # print(f'objj.filename_from_request: {objj.filename_from_request}')



    else:
        # DEBUG
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}
        return render(request, 'toolkit/calc_conflicts.html', context=data)


    #
    # all_files = UploadFiles2.objects.all()
    # for f in all_files:
    #     print(f'file: {f.file}')
    #     print(f'file: {f.file.url}')


    # with open(path_to_txt_conflicts_tmp, 'rb') as fw:
    #     f = SaveConflictsTXT(status_file='tesT', file=path_to_txt_conflicts_tmp)
    #     f.file.save(path_to_txt_conflicts_tmp, File(fw))

    # fw = open(path_to_txt_conflicts_tmp, 'rb')
    # f = SaveConflictsTXT(status_file='tesT', file=path_to_txt_conflicts_tmp)
    # f.file.save(path_to_txt_conflicts_tmp, File(fw))
    # fw.close()



    obj = conflicts.Conflicts()
    res, msg = obj.calculate_conflicts(input_stages=req_data.stages,
                                       controller_type=req_data.controller_type,
                                       make_txt_conflicts=req_data.val_txt_conflicts,
                                       add_conflicts_and_binval_calcConflicts=req_data.val_add_conflicts_and_binval_calcConflicts,
                                       make_config=req_data.val_make_config,
                                       prefix_for_new_config_file='New_',
                                       path_to_txt_conflicts=path_to_txt_conflicts,
                                       path_to_config_file=path_to_config_file)

    print(f'res: {res}: msg {msg}')
    print(f'obj.result_make_config.: {obj.result_make_config}')
    #

    print(f'obj.result_num_kolichestvo_napr: {obj.result_num_kolichestvo_napr}')
    print(f'sorted_stages: {obj.sorted_stages}')
    print(f'kolichestvo_napr: {obj.kolichestvo_napr}')
    print(f'matrix_output: {obj.matrix_output}')
    print(f'matrix_swarco_F997: {obj.matrix_swarco_F997}')
    print(f'conflict_groups_F992: {obj.conflict_groups_F992}')
    print(f'binary_val_swarco_for_write_PTC2: {obj.binary_val_swarco_for_write_PTC2}')
    print(f'binary_val_swarco_F009: {obj.binary_val_swarco_F009}')


    if obj.result_make_config and obj.result_make_config[0] and len(obj.result_make_config) >= 3:
        f = UploadFiles2(status_file='dest', group=2, file=obj.result_make_config[2])
        f.file.name = ProcessedRequestConflicts.correct_path(f.file.path)
        print(f'f.file.path: {f.file.path}')
        print(f'f.file.name: {f.file.name}')
        f.save()


    data = {
        'menu_header': menu_header,
        'title': title,
        'render_conflicts_data': res,
        'add_conflicts_and_binval_calcConflicts': req_data.val_add_conflicts_and_binval_calcConflicts,
        'values': ('| K|', '| O|'),
        'matrix': obj.matrix_output,
        'sorted_stages': obj.sorted_stages,
        'kolichestvo_napr': obj.kolichestvo_napr,
        'matrix_swarco_F997': obj.matrix_swarco_F997,
        'conflict_groups_F992': obj.conflict_groups_F992,
        'binary_val_swarco_F009': obj.binary_val_swarco_F009,
        'txt_conflict_file': SaveConflictsTXT.objects.last(),
        'config_file': UploadFiles2.objects.last(),
    }

    return render(request, 'toolkit/calc_conflicts.html', context=data)


def controller_swarco(request):
    data = {'title': 'Swarco', 'menu_header': menu_header}

    content = render_to_string('toolkit/swarco.html', data, request)

    return HttpResponse(content, )


    return render(request, 'toolkit/swarco.html', context=data, content_type='application/force-download')


def controller_peek(request):
    data = {'title': 'Peek', 'menu_header': menu_header}
    return render(request, 'toolkit/peek.html', context=data)


def controller_potok(request):
    data = {'title': 'Поток', 'menu_header': menu_header}
    return render(request, 'toolkit/potok.html', context=data)


def make_obj_snmp(protocol, ip_adress, scn=None):
    print(protocol, ip_adress)
    if protocol == 'Swarco_STCIP':
        print('11111')
        obj = snmpmanagement_v2.Swarco(ip_adress)
    elif protocol == 'Поток_STCIP':
        obj = snmpmanagement_v2.PotokS(ip_adress)
    elif protocol == 'Поток_UG405':
        obj = snmpmanagement_v2.Potok(ip_adress, scn)
    elif protocol == 'Peek_UG405':
        obj = None
    else:
        obj = None

    return obj

