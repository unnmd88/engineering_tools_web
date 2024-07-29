import os
from functools import reduce


def calculate_conflicts(stages=None, name_for_txt_conflicts=None, path_to_config_file=None,
                        controller_type=None, add_conflicts_and_binval_calcConflicts=False,
                        make_config=False):
    """ Функция формирует матрицу конфликтов на алгоритме поиска конфликтных направлений
        Матрица для функции F997 swarco: 0 индекс -> 1 направление, 1 индекс -> 2 направление и т.д.
        Матрица для вывода на экран(oputput)/записи в файл: 0 индекс -> шапка матрицы
        1 индекс -> 1 направление, 2 индекс -> 2 направление и т.д.
        Вазвращает кортеж списков: (матрица сварко(list), матрица output(list), бинарное значение для F009(list)
        matrix_swarco_F997 - > матрица конфликтов для F997
        matrix_output -> матрица конфликтов для записи в txt/вывода на экран
        binary_val_swarco_for_write_PTC2 -> бинарные значения фаз для записи в PTC2
        binary_val_swarco_F009 -> бинарные значения фаз для записи txt
        supervisor_matrix_swarco_F997 -> матрица конфликтов для F997, ссозданная на основе алгоритма, отличающегося
        от того, по которому формируется matrix_swarco_F997. После создания обеих матриц идёт проверка, равны
        ли они друг другу. Если не равны -> выходим из функции и пишем в лог

    """
    # print(f'ya v make_conflicts_and_binary_val')
    # print(stages)
    stages_and_napr = sort_stages(stages)
    # print(stages_and_napr)
    sorted_stages, kolichestvo_napr = stages_and_napr

    if sorted_stages is None or kolichestvo_napr is None:
        return
    if name_for_txt_conflicts is None:
        name_for_txt_conflicts = 'Calculate conflicts.txt'

    if controller_type is not None and make_config:
        if controller_type == 'swarco' and kolichestvo_napr > 48:
            return 'swarco more than 48 directions have been introduced'
        elif controller_type == 'swarco' and len(sorted_stages) > 8:
            return 'swarco more than 8 stages have been introduced'
        elif controller_type == 'peek' and kolichestvo_napr > 64:
            return 'peek more than 64 directions have been introduced'
        elif controller_type == 'peek' and len(sorted_stages) > 32:
            return 'peek more than 32 stages have been introduced'

    matrix_output, matrix_swarco_F997, binary_val_swarco_for_write_PTC2, \
        binary_val_swarco_F009 = make_conflicts_and_binary_val(sorted_stages, kolichestvo_napr)

    conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997, controller_type)

    if add_conflicts_and_binval_calcConflicts or make_config and controller_type == 'swarco':

        write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
                                    kolichestvo_napravleniy=kolichestvo_napr,
                                    sorted_stages=sorted_stages, matrix_output=matrix_output,
                                    conflicts_and_binVal_swarco=True,
                                    matrix_swarco_F997=matrix_swarco_F997,
                                    binary_val_swarco_F009=binary_val_swarco_F009,
                                    conflict_groups_F992=conflict_groups_F992)
    else:
        write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
                                    sorted_stages=sorted_stages,
                                    kolichestvo_napravleniy=kolichestvo_napr,
                                    matrix_output=matrix_output)

    if make_config:
        if controller_type == 'swarco':
            result_write_conflicts = make_PTC2_file(matrix_swarco_F997=matrix_swarco_F997,
                                                    binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
                                                    path_to_original_PTC2=path_to_config_file)
            return
        elif controller_type == 'peek':

            conflict_groups_F992, sum_conflicts = make_number_coflicts_group_for_swarco_F992(
                matrix_swarco_F997, controller_type)
            result_write_conflicts = make_dat_file_for_peek(
                conflict_groups_F992, sum_conflicts, sorted_stages, path_to_config_file)

    return sorted_stages, kolichestvo_napr, matrix_output, matrix_swarco_F997, conflict_groups_F992, \
        binary_val_swarco_for_write_PTC2, binary_val_swarco_F009

    # if flag_save_conflicts_to_PTC2:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009,
    #                             binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_save_conflicts_to_PTC2=True, path_to_original_PTC2=path_to_original_PTC2,
    #                             path_to_new_PTC2=path_to_config_file)
    # elif flag_save_conflicts_to_dat_peek:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009,
    #                             binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_save_conflicts_to_PTC2=False, path_to_original_PTC2=path_to_original_PTC2,
    #                             path_to_new_PTC2=path_to_config_file)
    #     make_dat_file_for_peek(conflict_groups_F992)
    #
    # elif conflicts_and_binVal_swarco_for_txt:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009, kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_conflicts_swarco=conflicts_and_binVal_swarco_for_txt
    #                             )
    # else:
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output,
    #                             )

    # if flag_conflicts_swarco:
    #     return matrix_swarco_F997, matrix_output,
    # conflicts_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)


class Conflicts:

    allowed_max_stages_swarco = 8
    allowed_max_kolichestvo_napr_swarco = 48
    allowed_max_num_stages_without_controller_type = 100

    allowed_max_stages_peek = 32
    allowed_max_kolichestvo_napr_peek = 64
    allowed_max_num_kolichestvo_napr_without_controller_type = 100



    available_controller_types = ['swarco', 'peek']


    msg_no_data_input_stages = 'Ошибка: Некорректный тип данных'
    msg_less_than_2_stages_input_stages = 'Ошибка: Дано менее двух фаз'
    msg_more_than_100_stages_input_stages = 'Ошибка: Дано более ста фаз!'

    msg_data_input_stages_success = 'Успех: проверка входных данных успешо пройдена'

    msg_controller_type_is_not_selected = 'Ошибка: Тип контроллера не выбран'



    msg_more_than_8_stages_swarco = 'Ошибка: Для контрллера swarco выбрано более 8 фаз'
    msg_more_than_32_stages_peek = 'Ошибка: Для контрллера peek выбрано более 32 фаз'
    msg_max_num_stages_success = 'Успех: проверка допустимого количества фаз успешо пройдена'

    msg_more_than_48_groups_swarco = 'Ошибка: Для контрллера swarco выбрано более 48 направлений'
    msg_more_than_64_groups_peek = 'Ошибка: Для контрллера peek выбрано более 64 направлений'
    msg_max_num_groups_success = 'Успех: проверка допустимого количества фаз успешо пройдена'

    msg_more_than_100_groups_without_controller_type = 'Ошибка: Дано более ста фаз!'



    def __init__(self, stages=None, controller_type=None, numCO=None):
        """
            Attributes:
                |--- matrix_swarco_F997 - > матрица конфликтов для F997 swarco
                |--- matrix_output -> матрица конфликтов для записи в txt/вывода на экран
                |--- binary_val_swarco_for_write_PTC2 -> бинарные значения фаз для записи в PTC2
                |--- binary_val_swarco_F009 -> бинарные значения фаз для записи txt
                |--- conflict_groups_Peek - > матрица конфликтов для peek
                |--- sum_conflicts_for_peek -> количество конфликтов для peek


                :param self.input_stages -> список списков от польщователя, на основе которого будет
                                            производится расчёт конфликтов и формироваться данные
                                            для вывода/конфига .PTC2(swarco) или .DAT(для peek)
        """
        self.numCO = numCO
        self.input_stages = None
        self.tmp_input_stages = None
        self.controller_type = controller_type

        self.sorted_stages = None
        self.matrix_output = None
        self.matrix_swarco_F997 = None
        self.binary_val_swarco_for_write_PTC2 = None
        self.binary_val_swarco_F009 = None
        self.conflict_groups_F992 = None
        self.conflict_groups_Peek = None
        self.sum_conflicts_for_peek = None
        self.num_stages = None
        self.kolichestvo_napr = 0
        self.sum_conflicts_for_peek = 0
        self.make_config = None

        self.add_conflicts_and_binval_calcConflicts = None


        self.result_make_txt = []
        self.result_make_config = []
        self.result_num_stages = []
        self.result_num_kolichestvo_napr = []
        self.result_input_data_stages = []


    def remove_quotes(self, user_file):
        """Функция принимает на вход строку, которую ввел пользователь, содержащую путь к каталогу/файлу и
           возвращает строку без кавычек"""
        user_file = user_file.replace('"', '').replace("'", '')
        return user_file

    def make_path_to_save_file(self, path_old: str, prefix: str = 'new_'):
        """
            Метод формирует и возвращает новый путь к файлу

        :param str path_old: Исходный путь к файлу
        :param str prefix: суффикс, который будет добавлен к названию нового файла
        :return str: новый путь
        """
        if '/' in path_old:
            part1_dir = '/'.join(path_old.split('/')[:-1])
            part2_name = '/'.join(path_old.split('/')[-1:])
            path = f'{part1_dir}/{prefix}{part2_name}'
        elif '\\' in path_old:
            path_old = self.remove_quotes(path_old)
            part1_dir = '\\'.join(path_old.split('\\')[:-1])
            part2_name = '\\'.join(path_old.split('\\')[-1:])
            path = f'{part1_dir}/{prefix}{part2_name}'
        else:
            path = 'Error creating a new file path'

        return path


    def validate_input_data_stages(self, input_data_stages):
        """"
            Метод проверяет, получены ли данных о фазах на вход функции calculate_conflicts
            Записывает в self.result_input_data_stages результат проверки в виде списка,
            где:
                self.result_input_data_stages[0] -> результат
                self.result_input_data_stages[1] -> сообщение(может быть использовано в дальнейшем)
            :param input_data_stages -> данные, список фаз
        """

        if isinstance(input_data_stages, str):
            input_data_stages = input_data_stages.split('\n')

        if not isinstance(input_data_stages, list):
            self.result_input_data_stages = (False, self.msg_no_data_input_stages)
            raise TypeError

        if len(input_data_stages) < 2:
            self.result_input_data_stages = (False, self.msg_less_than_2_stages_input_stages)
            return
        elif len(input_data_stages) > 100:
            self.result_input_data_stages = (False, self.msg_more_than_100_stages_input_stages)

        self.result_input_data_stages = (True, self.msg_data_input_stages_success)
        print(f'self.tmp_input_stages  from validate_input_data_stages: {self.tmp_input_stages}')
        return input_data_stages

    def validate_max_stages(self, stages, consider_controller_type=True, controller_type=None):
        """"
            Метод проверяет допустимое количество фаз
            Записывает в self.result_input_data_stages результат проверки в виде списка,
            где:
                result_num_stages[0] -> результат
                result_num_stages[1] -> сообщение(может быть использовано в дальнейшем)
            :param consider_controller_type -> учитывать ли тип контроллера при проверке
                                               максимально допустимого количества фаз
            :param controller_type -> тип контроллера, для которого необходимо рассчитать конфликты
        """
        num_stages = len(stages)
        self.num_stages = num_stages


        if consider_controller_type:
            if controller_type is None:
                self.result_num_stages = [False, self.msg_controller_type_is_not_selected]
                raise ValueError
            if controller_type == self.available_controller_types[0]:
                if num_stages > self.allowed_max_stages_swarco:
                    self.result_num_stages = [False, f'{self.msg_more_than_8_stages_swarco}: {num_stages}']
                else:
                    self.result_num_stages = [True, f'{self.msg_max_num_stages_success}']
            elif controller_type == self.available_controller_types[1]:
                if num_stages > self.allowed_max_stages_peek:
                    self.result_num_stages = [False, f'{self.msg_more_than_32_stages_peek}: {num_stages}']
                else:
                    self.result_num_stages = [True, f'{self.msg_max_num_stages_success}']
        else:
            if num_stages > self.allowed_max_num_stages_without_controller_type:
                self.result_num_stages = [False, f'{self.msg_more_than_100_stages_input_stages}: {num_stages}']
            else:
                self.result_num_stages = [True, f'{self.msg_max_num_stages_success}']

    def validate_max_groups(self, num_groups, consider_controller_type=True, controller_type=None):
        """"
            Метод проверяет допустимое количество направлений
            Записывает в self.result_num_kolichestvo_napr результат проверки в виде списка,
            где:
                result_num_kolichestvo_napr[0] -> результат
                result_num_kolichestvo_napr[1] -> сообщение(может быть использовано в дальнейшем)
            :param consider_controller_type -> учитывать ли тип контроллера при проверке
                                               максимально допустимого количества направлений
            :param controller_type -> тип контроллера, для которого необходимо рассчитать конфликты
        """

        if controller_type is None:
            self.result_num_kolichestvo_napr = [False, self.msg_controller_type_is_not_selected]
            raise ValueError

        if consider_controller_type:
            if controller_type == self.available_controller_types[0]:
                if num_groups > self.allowed_max_kolichestvo_napr_swarco:
                    self.result_num_kolichestvo_napr = [False, f'{self.msg_more_than_48_groups_swarco}: {num_groups}']
                else:
                    self.result_num_kolichestvo_napr = [True, f'{self.msg_max_num_groups_success}']
            elif controller_type == self.available_controller_types[1]:
                if num_groups > self.allowed_max_kolichestvo_napr_peek:
                    self.result_num_kolichestvo_napr = [False, f'{self.msg_more_than_64_groups_peek}: {num_groups}']
                else:
                    self.result_num_kolichestvo_napr = [True, f'{self.msg_max_num_groups_success}']
        else:
            if num_groups > self.allowed_max_num_kolichestvo_napr_without_controller_type:
                self.result_num_kolichestvo_napr = [False, f'{self.msg_more_than_100_groups_without_controller_type}: {num_groups}']
            else:
                self.result_num_kolichestvo_napr = [True, f'{self.msg_max_num_groups_success}: {num_groups}']

        return self.result_num_kolichestvo_napr[0]



    def sort_stages(self, stages, auto_correct=True,
                    chars_for_identification_all_red=('-', 'всем красный', 'кругом красный', '')):
        """
            Функция сортирует списки(list) фаза-направление.
            Вложенный список с индексом 0 -> 1 фаза, с индексом 1 -> 2 фаза и т.д.
            Значения в списке - направления, участвующие в фазе
        """

        # if self.input_stages is None or len(self.input_stages) > 255:
        #     return
        # self.sorted_stages = self.input_stages
        #
        # kolichestvo_naptavleniy = 0
        # for i in range(len(self.sorted_stages)):
        #     try:
        #         if self.sorted_stages[i][0].replace(' ', '') != '':
        #             self.sorted_stages[i] = list(map(int, self.sorted_stages[i]))
        #             max_num_napr_v_faze = max(self.sorted_stages[i])
        #             if kolichestvo_naptavleniy < max_num_napr_v_faze:
        #                 kolichestvo_naptavleniy = max_num_napr_v_faze
        #             self.sorted_stages[i] = sorted(list(set(self.sorted_stages[i])))
        #         else:
        #             self.sorted_stages[i] = []
        #     except ValueError as err:
        #         return err
        #
        # self.kolichestvo_napr = kolichestvo_naptavleniy
        # return




        # Новый вариант, с проверкой
        self.sorted_stages = []
        self.kolichestvo_napr = 0


        # stages_tmp = self.input_stages.split('\n')
        print(f'stages из метода, начало алгоритма сортировки: {stages}')
        for line in stages:
            if ':' in line:
                processed_line = line.replace("\r", '').split(':')[1]
            else:
                processed_line = line.replace("\r", '')
            processed_line = processed_line.replace(" ", '')

            print(f'processed_line xxxccc: {processed_line}')
            if processed_line in chars_for_identification_all_red:
                self.sorted_stages.append([])
                continue

            print(f'processed_line до split ",": {processed_line}')
            processed_line = list(set(processed_line.split(',')))
            print(f'processed_line после split и sort",": {processed_line}')
            # Проверка корректности введенных данных
            for i, char in enumerate(processed_line):
                if not char.isdigit():
                    raise ValueError
                else:
                    processed_line[i] = int(char)

            processed_line = sorted(processed_line)

            print(f'processed_line: {processed_line}')
            self.sorted_stages.append(processed_line)

            if processed_line[-1] > self.kolichestvo_napr:
                self.kolichestvo_napr = processed_line[-1]

            if not self.validate_max_groups(self.kolichestvo_napr, controller_type=self.controller_type):
                return False




        print(f'self.sorted_stages final: {self.sorted_stages}')
        print(f'self.kolichestvo_naptavleniy: {self.kolichestvo_napr}')
        return True



    def make_conflicts_and_binary_val(self, confl_swarco='03.0;'):
        """"
            В даном методе производится расчёт кофликтов и формируется имнформация для вывода
            пользователю/записи в текстовый файл/формирования кофигов(swarco и peek)
            В методе реализовано 2 различных алгоритма по формированию конфликтов, в конце которых прозволится
            проверка на совпдаение расчётов конфликтов. Если итоговые расёты не совпадают, то функция
            возвращает строку 'Error of correct calculation', иначе вернёт True
            supervisor_matrix_swarco_F997 -> матрица конфликтов для F997, ссозданная на основе алгоритма, отличающегося
            от того, по которому формируется matrix_swarco_F997. После создания обеих матриц идёт проверка, равны
            ли они друг другу.

            :param confl_swarco -> згачение, которым будет заполнена матрица, когда есть конфликт

            :return str -> 'Error of correct calculation' если итоговые расёты не совпадают,
            :return bool -> True, если расчёты совпали
        """

        self.matrix_swarco_F997 = []
        self.binary_val_swarco_for_write_PTC2 = []
        self.binary_val_swarco_F009 = []
        supervisor_matrix_swarco_F997 = []
        # Шапка вида | *| |01| |02| |03| |04| |05| |06| |07| |08| |09| |10|
        self.matrix_output = [['| *|' if i == 0 else f'|0{i}|' if i < 10 else f'|{i}|' for i in range(self.kolichestvo_napr + 1)]]

        for i in range(1, self.kolichestvo_napr + 1):
            tmp_matrix_output = ['X;' if x == i - 1 else confl_swarco for x in range(self.kolichestvo_napr)]
            tmp_matrix_swarco_F997 = [f'|0{i}|' if x == 0 and i < 10 else f'|{i}|' if x == 0 and i > 9 else
            '| K|' for x in range(self.kolichestvo_napr + 1)]
            binary_val = 0

            tmp_for_supervisor = []
            tmp_matrix_swarco_F997_supervosor = ['X;' if x == i - 1 else confl_swarco for x in range(self.kolichestvo_napr)]

            for j in range(len(self.sorted_stages)):
                if i in self.sorted_stages[j]:
                    for napr in self.sorted_stages[j]:
                        tmp_matrix_output[napr - 1] = '  . ;'
                        tmp_matrix_output[i - 1] = 'X;'

                        tmp_matrix_swarco_F997[napr] = '| O|'
                        tmp_matrix_swarco_F997[i] = '| *|'
                        # Для проверки(supervisor_matrix_swarco_F997)
                        tmp_for_supervisor = tmp_for_supervisor + self.sorted_stages[j]

                    if j != 7:
                        binary_val = binary_val + 2 ** (j + 1)
                    else:
                        binary_val = binary_val + 2 ** 0
                # Если фаза пустая(без направлений)
                elif i not in self.sorted_stages[j]:
                    tmp_matrix_swarco_F997[i] = '| *|'

            if binary_val < 10:
                self.binary_val_swarco_for_write_PTC2.append([f';00{binary_val};;1;'])
            elif binary_val > 9 and binary_val < 100:
                self.binary_val_swarco_for_write_PTC2.append([f';0{binary_val};;1;'])
            elif binary_val > 99 and binary_val < 256:
                self.binary_val_swarco_for_write_PTC2.append([f';{binary_val};;1;'])
            self.binary_val_swarco_F009.append([f'{binary_val};'])

            self.matrix_swarco_F997.append(tmp_matrix_output)
            self.matrix_output.append(tmp_matrix_swarco_F997)

            # Для проверки(supervisor_matrix_swarco_F997)
            tmp_for_supervisor = sorted(list(set(tmp_for_supervisor)))
            for ii in tmp_for_supervisor:
                tmp_matrix_swarco_F997_supervosor[ii - 1] = '  . ;'
                tmp_matrix_swarco_F997_supervosor[i - 1] = 'X;'
            supervisor_matrix_swarco_F997.append(tmp_matrix_swarco_F997_supervosor)

        if supervisor_matrix_swarco_F997 != self.matrix_swarco_F997:
            return 'Error of correct calculation'
        else:
            return True

    def make_number_coflicts_group_for_swarco_F992(self):
        """ Функция принимает на вход матрицу конфликтов вида F997.
            Рассчитывает и возвращает вложенный список направлений, с которыми есть конфликт у каждой их групп
            Вложенный список с индеком 0 -> группы, с которыми есть конфликт у 1 направления,
            индекс 1 -> группы, с которыми есть конфликт у 2 направления и т.д.
        """

        if self.controller_type == 'swarco':
            self.conflict_groups_F992 = []
            for i in range(len(self.matrix_swarco_F997)):
                tmp = []
                num_group = 1

                for j in self.matrix_swarco_F997[i]:
                    if j == '03.0;':
                        tmp.append(f'{num_group};')
                    num_group += 1
                self.conflict_groups_F992.append(tmp)

        elif self.controller_type == 'peek':
            self.conflict_groups_Peek = []
            self.sum_conflicts_for_peek = 0

            for i in range(len(self.matrix_swarco_F997)):
                tmp2 = []
                num_group = 1
                for j in self.matrix_swarco_F997[i]:
                    if j == '03.0;':
                        tmp2.append(num_group)
                    num_group += 1
                self.conflict_groups_Peek.append(tmp2)
                self.sum_conflicts_for_peek = self.sum_conflicts_for_peek + len(tmp2)



    def calculate_conflicts(self, path_to_txt_conflicts=None, path_to_config_file=None, prefix_for_new_file='new_',
                            add_conflicts_and_binval_calcConflicts=False,
                            make_config=False,
                            controller_type=None,
                            input_stages=None):
        """ Функция формирует матрицу конфликтов на основе алгоритма поиска конфликтных направлений
            Матрица для функции F997 swarco: 0 индекс -> 1 направление, 1 индекс -> 2 направление и т.д.
            Матрица для вывода на экран(oputput)/записи в файл: 0 индекс -> шапка матрицы
            1 индекс -> 1 направление, 2 индекс -> 2 направление и т.д.

            supervisor_matrix_swarco_F997 -> матрица конфликтов для F997, ссозданная на основе алгоритма, отличающегося
            от того, по которому формируется matrix_swarco_F997. После создания обеих матриц идёт проверка, равны
            ли они друг другу. Если не равны -> выходим из функции и пишем в лог

        """

        self.input_stages = input_stages
        print(f'self.input_stages):{self.input_stages}')
        print(f'type self.input_stages):{type(self.input_stages)}')
        self.controller_type = controller_type
        self.make_config = make_config

        print(f'if isinstance(self.tmp_input_stages, str):{isinstance(self.tmp_input_stages, str)}')
        if isinstance(self.input_stages, str):
            self.tmp_input_stages = input_stages.split('\n')
        elif not isinstance(self.tmp_input_stages, list):
            raise ValueError

        # Первая проверка на корректность входных данных в input_stages
        result = self.validate_input_data_stages(input_stages)
        if self.result_input_data_stages[0]:
            self.tmp_input_stages = result
        else:
            return self.result_input_data_stages[1]
        # Вторая проверка на максимально допустимое количество фаз
        self.validate_max_stages(self.tmp_input_stages, controller_type=self.controller_type)

        # Сортировка фаз(направления по возврастанию/выбрасывание дублей/символов, проверка корректности данных)
        # Третья проверка на максимально допустимое количество направлений внутри self.sort_stages()
        if not self.sort_stages(self.tmp_input_stages):
            return self.result_num_kolichestvo_napr

        if path_to_txt_conflicts is None:
            path_to_txt_conflicts = 'Calculate conflicts.txt'


        self.make_conflicts_and_binary_val()
        self.make_number_coflicts_group_for_swarco_F992()

        if add_conflicts_and_binval_calcConflicts or make_config and self.controller_type == 'swarco':
            result_make_txt = self.write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=path_to_txt_conflicts,
                                                               conflicts_and_binVal_swarco=True,)
        else:
            result_make_txt = self.write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=path_to_txt_conflicts)

        if make_config:
            if self.controller_type == 'swarco':
                result_make_config = self.make_PTC2_file(path_to_original_PTC2=path_to_config_file,
                                                         prefix_for_new_file=prefix_for_new_file)
            elif self.controller_type == 'peek':
                result_make_config = self.make_dat_file_for_peek(path_to_original_DAT=path_to_config_file,
                                                                 prefix_for_new_file=prefix_for_new_file)
            else:
                result_make_config = 'Config file not created'
            return result_make_txt, result_make_config
        else:
            return result_make_txt

        # return 'Txt file not created', 'Config file not created'

    def write_conflicts_to_txt_file(self, path_and_name_for_txt_conflicts=None, conflicts_and_binVal_swarco=False):
        """Функция производит запись вычесленных ранее ""Матрица конфликтов "интергрин" F997",
           "Физические конфликты - номера конфликтных групп F992", "Сигнальные группы в фазах F009"(бинарные значения)
           в файл по указанному пользевателем каталогу

        :return bool -> True, если файл с конфликтами создан, иначе False
        :return str -> Ошибка из except

        """
        # Запись значений в файл
        try:
            with open(path_and_name_for_txt_conflicts, 'w') as file:
                # Запишем в файл общую информацию: Фазы-Направления
                num_stage = 1
                for stage in self.sorted_stages:
                    if stage:
                        file.write(f"Фаза {num_stage}: ")
                        check_last_item = 1
                    else:
                        file.write(f"Фаза {num_stage}:\n")
                        num_stage += 1
                        continue
                    for num_napravleniya in stage:
                        if check_last_item == len(stage):
                            file.write(f'{num_napravleniya}\n')
                        else:
                            file.write(f'{num_napravleniya}, ')
                            check_last_item += 1
                    num_stage += 1
                file.write(f'Количество направлений: {self.kolichestvo_napr}\n\n')

                # Общая "Матрица конфликтов"
                for stroka_napravleine in range(self.kolichestvo_napr + 1):
                    file.write(f'{" ".join(self.matrix_output[stroka_napravleine])}\n')
                file.write('\n')

                if not conflicts_and_binVal_swarco:
                    return True
                # Запишем в файл "Матрица конфликтов "интергрин" F997"
                file.write('Матрица конфликтов "интергрин" F997:\n')
                for num_napravleniya in self.matrix_swarco_F997:
                    for stroka_napravlenie in num_napravleniya:
                        file.write(stroka_napravlenie)
                    file.write('\n')
                file.write('\n')

                # Запишем в файл "Физические конфликты - номера конфликтных групп F992"
                file.write('Физические конфликты - номера конфликтных групп F992:\n')
                for num_napravleniya in self.conflict_groups_F992:
                    for stroka_napravlenie in num_napravleniya:
                        file.write(stroka_napravlenie)
                    file.write('\n')
                file.write('\n')

                # Запишем в файл "Сигнальные группы в фазах F009"(,бинарные значения)
                file.write('Сигнальные группы в фазах F009: \n')
                for num_napravleniya in self.binary_val_swarco_F009:
                    for val in num_napravleniya:
                        file.write(val)
                if os.path.exists(path_and_name_for_txt_conflicts):
                    result = 'the file was created successfully'
                else:
                    result = 'Error: the file was not created'
                return result
        except Exception as err: # определить какую ошибку ловишь
            pass #что-то делать
            return err # например

    def make_PTC2_file(self, path_to_original_PTC2, prefix_for_new_file: str, ):
        """
        Метод создает новый .PTC2 файл с рассчитанными конфликтами и фазами
        :param path_to_original_PTC2: путь к исходному файлу, на основе которого будет сформирован новый
        :return str: сообщение
        """
        path_to_new_PTC2 = self.make_path_to_save_file(path_to_original_PTC2, prefix=prefix_for_new_file)

        try:
            with open(path_to_original_PTC2) as file, open(path_to_new_PTC2, 'w') as new_file:
                flag1 = flag2 = flag3 = flag4 = False
                for line in file:
                    if flag1:
                        if 'NeXt' not in line:
                            new_file.write('')
                        else:
                            flag1 = False
                    elif flag2:
                        if 'NeXt' not in line:
                            new_file.write('')
                        else:
                            flag2 = False
                    elif flag3:
                        if 'NeXt' not in line:
                            new_file.write('')
                        else:
                            flag3 = False
                    elif flag4:
                        if 'NeXt' not in line:
                            new_file.write('')
                        else:
                            flag4 = False

                    if 'NewSheet693  : Work.997' in line:
                        flag1 = True
                        new_file.write(line)
                        for group_line in self.matrix_swarco_F997:
                            new_file.write(''.join(group_line))
                            new_file.write('\n')
                    elif 'NewSheet693  : Work.992' in line:
                        flag2 = True
                        new_file.write(line)
                        for group_line in self.matrix_swarco_F997:
                            new_file.write(''.join(group_line))
                            new_file.write('\n')
                    elif 'NewSheet693  : Work.009' in line:
                        flag3 = True
                        new_file.write(line)
                        for group_line in self.binary_val_swarco_for_write_PTC2:
                            new_file.write(''.join(group_line))
                            new_file.write('\n')
                    elif 'NewSheet693  : Work.006' in line:
                        flag4 = True
                        new_file.write(line)
                    elif not flag1 and not flag2 and not flag3 and not flag4:
                        new_file.write(line)
                if os.path.exists(path_to_new_PTC2):
                    result = 'the file was created successfully'
                else:
                    result = 'Error: the file was not created'
                return result
        except Exception as err:  # определить какую ошибку ловишь
            pass  # что-то делать
            return err  # например

    def make_dat_file_for_peek(self, path_to_original_DAT: str, prefix_for_new_file: str = 'new_'):
        sum_stages = len(self.sorted_stages)
        new_file_dat = self.make_path_to_save_file(path_to_original_DAT, prefix=prefix_for_new_file)

        table_conflicts = f':TABLE "XSGSG",{str(self.sum_conflicts_for_peek)},4,3,4,4,3\n'
        table_SA_STG = f':TABLE "YSRM_SA_STG",{str(sum_stages)},2,4,10\n'
        table_UK_STAGE = f':TABLE "YSRM_UK_STAGE",{str(sum_stages)},4,4,4,1,10\n'

        try:
            with open(path_to_original_DAT, 'r', encoding='utf-8') as file1, open(new_file_dat, 'w',
                                                                                  encoding='utf-8') as file2:
                flag1 = flag2 = flag3 = False
                count = 0
                for line in file1:
                    if flag1 and 'TABLE "YKLOK"' not in line:
                        pass
                    elif flag1 and 'TABLE "YKLOK"' in line:
                        flag1 = False
                        count += 1
                        file2.write(':END\n')
                        file2.write(line)
                    elif ':TABLE "XSGSG"' in line:
                        file2.write(table_conflicts)
                        for num_group_from in range(len(self.conflict_groups_Peek)):
                            for num_group_to in self.conflict_groups_Peek[num_group_from]:
                                file2.write(f':RECORD\n'
                                            f'"Type",2\n'
                                            f'"Id1",{str(num_group_from + 1)}\n'
                                            f'"Id2",{str(num_group_to)}\n'
                                            f'"Time",30\n'
                                            f':END\n')
                        flag1 = True

                    elif flag2 and ':TABLE "YSRM_STEP"' not in line:
                        pass
                    elif flag2 and ':TABLE "YSRM_STEP"' in line:
                        flag2 = False
                        count += 1
                        file2.write(':END\n')
                        file2.write(line)
                    elif ':TABLE "YSRM_SA_STG"' in line:
                        file2.write(table_SA_STG)
                        for num_stage in range(len(self.sorted_stages)):
                            stage = ','.join(list(map(str, self.sorted_stages[num_stage])))
                            file2.write(f':RECORD\n'
                                        f'"Id",{str(num_stage + 1)}\n'
                                        f'"SGdef","{stage}"\n'
                                        f':END\n')
                        flag2 = True

                    elif flag3 and '"YSRM_UK_STAGE_TRANS"' not in line:
                        pass
                    elif flag3 and '"YSRM_UK_STAGE_TRANS"' in line:
                        flag3 = False
                        count += 1
                        file2.write(':END\n')
                        file2.write(line)
                    elif ':TABLE "YSRM_UK_STAGE"' in line:
                        file2.write(table_UK_STAGE)
                        for num_stage in range(len(self.sorted_stages)):
                            stage = ','.join(list(map(str, self.sorted_stages[num_stage])))
                            file2.write(f':RECORD\n'
                                        f'"ProcessId",1\n'
                                        f'"StageId",{str(num_stage + 1)}\n'
                                        f'"StartUpStage",{str(True) if num_stage == 0 else str(False)}\n'
                                        f'"SignalGroups",",{stage},"\n'
                                        f':END\n')
                        flag3 = True

                    else:
                        file2.write(line)

            if os.path.exists(new_file_dat):
                result = 'the file was created successfully'
            else:
                result = 'Error: the file was not created'
            return result
        except Exception as err:  # определить какую ошибку ловишь
            pass  # что-то делать
            return err  # например