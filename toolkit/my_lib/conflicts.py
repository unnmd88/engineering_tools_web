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
    def __init__(self, stages):
        self.input_stages = stages
        self.sorted_stages = self.matrix_output = self.matrix_swarco_F997 = self.binary_val_swarco_for_write_PTC2 = \
            self.binary_val_swarco_F009 = self.conflict_groups_F992 = []
        self.conflict_groups_Peek = self.sum_conflicts_for_peek = []
        self.sum_conflicts_for_peek = 0
        self.matrix_output = []
        self.kolichestvo_napr = 0
        self.controller_type = None



    def sort_stages(self):
        """Функция сортирует списки фаза-направление. на вход получает список вложенных списков.
            Вложенный список с индексом 0 -> 1 фаза, с индексом 1 -> 2 фаза и т.д.
            Значения в списке - направления, участвующие в фазе
            Возвращает кортеж: отсортированный список списков фаза-направление, количество направлений
        """

        if self.input_stages is None or len(self.input_stages) > 255:
            return
        self.sorted_stages = self.input_stages

        kolichestvo_naptavleniy = 0
        for i in range(len(self.sorted_stages)):
            try:
                if self.sorted_stages[i][0].replace(' ', '') != '':
                    self.sorted_stages[i] = list(map(int, self.sorted_stages[i]))
                    max_num_napr_v_faze = max(self.sorted_stages[i])
                    if kolichestvo_naptavleniy < max_num_napr_v_faze:
                        kolichestvo_naptavleniy = max_num_napr_v_faze
                    self.sorted_stages[i] = sorted(list(set(self.sorted_stages[i])))
                else:
                    self.sorted_stages[i] = []
            except ValueError as err:
                return err

        self.kolichestvo_napr = kolichestvo_naptavleniy


    def make_conflicts_and_binary_val(self, confl_swarco='03.0;'):
        self.sorted_stages = self.matrix_output = self.matrix_swarco_F997 = self.binary_val_swarco_for_write_PTC2 = \
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
            return
        else:
            return

    def make_number_coflicts_group_for_swarco_F992(self):
        """ Функция принимает на вход матрицу конфликтов вида F997.
            Рассчитывает и возвращает вложенный список направлений, с которыми есть конфликт у каждой их групп
            Вложенный список с индеком 0 -> группы, с которыми есть конфликт у 1 направления,
            индекс 1 -> группы, с которыми есть конфликт у 2 направления и т.д.
        """

        if self.controller_type == 'swarco':
            self.conflict_groups_F992 = []
            # print('conflict_matrix_F997')
            # print(conflict_matrix_F997)
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
            # print('conflict_matrix_F997')
            # print(conflict_matrix_F997)
            self.sum_conflicts_for_peek = 0  # Количество конфликтов для Пика

            for i in range(len(self.matrix_swarco_F997)):
                tmp2 = []
                num_group = 1
                for j in self.matrix_swarco_F997[i]:
                    if j == '03.0;':
                        tmp2.append(num_group)
                    num_group += 1
                self.conflict_groups_Peek.append(tmp2)
                self.sum_conflicts_for_peek = self.sum_conflicts_for_peek + len(tmp2)
            # print('make_number_coflicts_group_for_swarco_F992')
            # print(conflict_groups_Peek)
            # print(f'sum_conflicts_for_peek: {sum_conflicts_for_peek}')
            # make_dat_file_for_peek(conflict_groups_F992, sum_conflicts_for_peek)


    def calculate_conflicts(self, name_for_txt_conflicts=None, path_to_config_file=None,
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
        self.sort_stages()


        if self.sorted_stages is None or self.kolichestvo_napr is None:
            return
        if name_for_txt_conflicts is None:
            name_for_txt_conflicts = 'Calculate conflicts.txt'

        if controller_type is not None and make_config:
            if controller_type == 'swarco' and self.kolichestvo_napr > 48:
                return 'swarco more than 48 directions have been introduced'
            elif controller_type == 'swarco' and len(self.sorted_stages) > 8:
                return 'swarco more than 8 stages have been introduced'
            elif controller_type == 'peek' and self.kolichestvo_napr > 64:
                return 'peek more than 64 directions have been introduced'
            elif controller_type == 'peek' and len(self.sorted_stages) > 32:
                return 'peek more than 32 stages have been introduced'


        self.make_conflicts_and_binary_val()
        self.make_number_coflicts_group_for_swarco_F992()

        if add_conflicts_and_binval_calcConflicts or make_config and self.controller_type == 'swarco':

            self.write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
                                             conflicts_and_binVal_swarco=True,)

        else:
            self.write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts)

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

        # return sorted_stages, kolichestvo_napr, matrix_output, matrix_swarco_F997, conflict_groups_F992, \
        #     binary_val_swarco_for_write_PTC2, binary_val_swarco_F009

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

    def write_conflicts_to_txt_file(self, path_and_name_for_txt_conflicts=None, conflicts_and_binVal_swarco=False):
        """Функция производит запись вычесленных ранее ""Матрица конфликтов "интергрин" F997",
           "Физические конфликты - номера конфликтных групп F992", "Сигнальные группы в фазах F009"(бинарные значения)
           в файл по указанному пользевателем каталогу"""
        # Запись значений в файл

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
            return True