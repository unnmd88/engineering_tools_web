import time
import datetime
import keyboard

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

import sdp_func_lib
import configuration


class PeekWeb:
    def __init__(self, ip_adress):
        self.ip_adress = ip_adress

        self.short_pause = 0.5
        self.middle_pause = 1
        self.long_pause = 4
        # print(f'timeout из init:')
        # print(f'self.short_pause: {self.short_pause}')
        # print(f'self.middle_pause: {self.middle_pause}')
        # print(f'self.long_pause: {self.long_pause}')

        # span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'   оригинал :)
        ###########################################################################################

    @staticmethod
    def _check_options_for_session(inputs, user_parameters, kwargs) -> tuple:
        """ Метод, который определяет, какие действия будут сорешаться в web сессии. Если inputs не None или
            в kwargs есть какой нибудь MPP_, то flag_user_inputs ставим в True. Аналогично для user_parameters
         """
        flag_user_inputs = flag_user_parameters = False
        # print(f'user_parameters: {user_parameters}')
        # print(f'inputs: {inputs}')
        # print(f'kwargs: {kwargs}')

        if inputs is not None:
            flag_user_inputs = True
        elif kwargs is not None:
            for key in kwargs:
                if 'MPP_' in key or 'CP_' in key:
                    flag_user_inputs = True
                    break
        else:
            flag_user_inputs = False

        if user_parameters is not None:
            flag_user_parameters = True
        elif kwargs is not None:
            for key in kwargs:
                if 'UP_' in key:
                    flag_user_parameters = True
                    break
        else:
            flag_user_parameters = False

        return flag_user_inputs, flag_user_parameters

    @staticmethod
    def _check_mpp_for_reset(name, state, actuator_val, required_actuator_values, session_for_greenroad):

        if not session_for_greenroad or not ('MPP_PH' in name):
            return False

        if actuator_val in required_actuator_values:
            return True
        if state == '1' and actuator_val != 'ВЫКЛ':
            return True

        return False

    @staticmethod
    def _make_dict_with_filtered_inputs_and_values(inputs_from_inputs, inputs_from_kwargs) -> dict:
        """ Метод, формирующий словарь с валидными Вводами и занчениями, которые будут установлены в скрипте
            обходом циклом for.
            dict inputs_from_inputs -> словарь, переданный в метод session_refactor. Если он не None,
            формируем новый словарь фильтрованных вводов на основе него. Если inputs_from_inputs = None,
            тогда формируем новый словарь фильтрованных вводов на основе inputs_from_kwargs(kwargs,
            переданные в метод session_refactor
            inputs_from_kwargs:
            :param dict inputs_from_inputs: словарь, переданный в метод session_refactor.
            :param inputs_from_kwargs: kwargs, переданные в метод session_refactor
        """

        actuator_values = {
            'ВФ': '//*[@id="button_div"]/ul/li[1]/button',
            'ВЫКЛ': '//*[@id="button_div"]/ul/li[2]/button',
            'ВКЛ': '//*[@id="button_div"]/ul/li[3]/button'
        }

        allowed_inputs = ('MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
                          'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
                          'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
                          'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO')

        filtered_inputs_to_set = dict()
        if inputs_from_inputs is not None:
            for k, v in inputs_from_inputs.items():
                # print(f'k: {k}->тип:{type(k)}, v: {v}')
                if k in allowed_inputs and v in actuator_values:
                    filtered_inputs_to_set[k] = v
        elif inputs_from_kwargs is not None:
            for k, v in inputs_from_kwargs.items():
                # print(f'k: {k}->тип:{type(k)}, v: {v}')
                if k in allowed_inputs and v in actuator_values:
                    filtered_inputs_to_set[k] = v
        return filtered_inputs_to_set

    @staticmethod
    def _make_dict_with_filtered_up_and_up_values(user_parameters_from_user_parameters, user_parameters_from_kwargs):
        """ Метод, формирующий словарь с валидными параметрами программы(юзер-параметрами и занчениями,
            которые будут установлены в скрипте
            обходом циклом for.
            dict user_parameters_from_user_parameters -> словарь, переданный в метод session_refactor. Если он не None,
            формируем новый словарь фильтрованных вводов на основе него. Если user_parameters_from_user_parameters = None,
            тогда формируем новый словарь фильтрованных вводов на основе inputs_from_kwargs(kwargs,
            переданные в метод session_refactor
            user_parameters_from_kwargs:
            :param dict user_parameters_from_user_parameters: словарь, переданный в метод session_refactor.
            :param user_parameters_from_kwargs: kwargs, переданные в метод session_refactor
        """
        # print('ya v _make_dict_with_filtered_up_and_up_values')
        filtered_user_parameters_to_set = dict()
        if user_parameters_from_user_parameters is not None:
            for k, v in user_parameters_from_user_parameters.items():
                # print(f'k: {k}->тип:{type(k)}, v: {v}')
                k = k.split('_')[1]
                if not k.isdigit() and not v.isdigit():
                    continue
                else:
                    v = str(v)
                    filtered_user_parameters_to_set[k] = list(v)

        elif user_parameters_from_kwargs is not None:
            for k, v in user_parameters_from_kwargs.items():
                # print(f'k: {k}->тип:{type(k)}, v: {v}')
                k = k.split('_')[1]
                if not k.isdigit() and not v.isdigit():
                    continue
                else:
                    v = str(v)
                    filtered_user_parameters_to_set[k] = tuple(v)
        # print(f'filtered_user_parameters_to_set: {filtered_user_parameters_to_set}')
        return filtered_user_parameters_to_set

    def _start_and_login(self, driver):
        """ Метод, в котором производится нажатие в нужные элементы чтобы залогинится """

        button_3_entrance = '//*[@id="buttonpad"]/form[1]/ul[1]/li[3]/button'
        button_entrance = '//*[@id="buttonpad"]/form[1]/ul[4]/li/button'


        time.sleep(self.middle_pause)
        driver.switch_to.parent_frame()
        driver.switch_to.frame('menu_frame')

        ### Пример поиска элемента
        # content = driver.find_elements(By.TAG_NAME, "span")
        # content = [el.text for el in content]
        # print(content)

        element = driver.find_element(By.TAG_NAME, 'ul')
        element = element.find_elements(By.TAG_NAME, 'li')
        main_page = [el.text for el in element]

        if 'Рисунок перекрёстка' in main_page:
            span_entrance = f'//*[@id="mainnav"]/li[3]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[7]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[6]/ul/li[3]/a/span'
        else:
            span_entrance = '//*[@id="mainnav"]/li[2]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[5]/ul/li[3]/a/span'
        # Клик в Вход
        element_input = driver.find_element(By.XPATH, span_entrance)
        element_input.click()
        time.sleep(self.middle_pause)
        # Логинимся 3333
        driver.switch_to.parent_frame()
        driver.switch_to.frame('content_frame')
        element_input = driver.find_element(By.XPATH, button_3_entrance)
        for i in range(4):
            element_input.click()
        element_input = driver.find_element(By.XPATH, button_entrance)
        element_input.click()
        time.sleep(self.middle_pause)

        return span_user_inputs, span_user_parameters

    def _click_to_mpp_inputs(self, driver, inputs: list, actuator: str):
        """" Метод, в котором осуществляется устанавливается нужное значение для нужных Вводов
            :param list inputs: список Вводов, в которые надо кликнуть.
            :param str actuator: значение актуатора, в которое надо кликнуть
        """
        # print('в _click_to_mpp_inputs')

        time.sleep(self.short_pause)
        for inp in inputs:
            # print(f'inp: {inp}')
            # Двойной клик в нужный вход в колонке АКТУАТОР:
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
            element_input = driver.find_element(By.XPATH, inp)
            action = ActionChains(driver)
            action.double_click(element_input)
            action.perform()
            time.sleep(self.middle_pause)
            # Клик в АКТУАТОР(ВКЛ/ВЫКЛ/ВФ)
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, actuator)))
            element_input = driver.find_element(By.XPATH, actuator)
            element_input.click()
            time.sleep(self.middle_pause)

    def _set_reset_cp_auto(self, driver, inputs_from_web):
        """ Метод, в котором производится клик сначала в CP_AUTO = ВКЛ, затем CP_AUTO = ВФ.
            Может применяться, например, если надо сбросить CP_RED(вывести в режим из Кругом красный).
            Т.е. после того, как сделан сброс CP_RED = ВФ, необходимо активировать CP_AUTO, чтобы котнтроллер
            перешёл в режим "УПРАВЛЕНИЕ"
            :param dict inputs_from_web: словарь с Вводами и их номера текущей вебки
        """

        # print('старт _set_reset_mpp_AUTO')

        actuator_SET = '//*[@id="button_div"]/ul/li[3]/button'
        actuator_RESET = '//*[@id="button_div"]/ul/li[1]/button'

        num_input = inputs_from_web.get('CP_AUTO')

        # Двойной клик в CP_AUTO в колонке АКТУАТОР:
        element_input = driver.find_element(By.XPATH, f'//*[@id="data"]/table/tbody/tr[{num_input}]/td[5]')
        action = ActionChains(driver)
        action.double_click(element_input)
        action.perform()
        time.sleep(self.middle_pause)
        # Клик в АКТУАТОР ВКЛ
        element_input = driver.find_element(By.XPATH, actuator_SET)
        element_input.click()
        time.sleep(self.middle_pause)
        # Двойной клик в CP_AUTO в колонке АКТУАТОР:
        element_input = driver.find_element(By.XPATH, f'//*[@id="data"]/table/tbody/tr[{num_input}]/td[5]')
        action = ActionChains(driver)
        action.double_click(element_input)
        action.perform()
        time.sleep(self.middle_pause)
        # Клик в АКТУАТОР ВКЛ
        element_input = driver.find_element(By.XPATH, actuator_RESET)
        element_input.click()
        time.sleep(self.middle_pause)
        print('финал _set_reset_mpp_AUTO')

    def _click_to_up_and_val_up(self, driver, filtered_user_parameters_to_set):
        """ Метод, в котором осуществляется клик в нужное значение нужного параметра программы(юзер-параметра)
            В цикле for на каждой итерации осуществляется клик в парметр программы(по индексу), который
            является ключом словаря, затем клик в значение(значение словаря)
            :param dict filtered_user_parameters_to_set: словарь с офтильтрованнами параметрами программы.
        """

        button_1_UP = '//*[@id="buttonpad"]/ul[1]/li[1]/button'
        button_2_UP = '//*[@id="buttonpad"]/ul[1]/li[2]/button'
        button_3_UP = '//*[@id="buttonpad"]/ul[1]/li[3]/button'
        button_4_UP = '//*[@id="buttonpad"]/ul[2]/li[1]/button'
        button_5_UP = '//*[@id="buttonpad"]/ul[2]/li[2]/button'
        button_6_UP = '//*[@id="buttonpad"]/ul[2]/li[3]/button'
        button_7_UP = '//*[@id="buttonpad"]/ul[3]/li[1]/button'
        button_8_UP = '//*[@id="buttonpad"]/ul[3]/li[2]/button'
        button_9_UP = '//*[@id="buttonpad"]/ul[3]/li[3]/button'
        button_0_UP = '//*[@id="buttonpad"]/ul[4]/li[1]/button'
        button_OK_UP = '//*[@id="buttonpad"]/ul[4]/li[4]/button'

        buttons = {'1': button_1_UP, '2': button_2_UP, '3': button_3_UP,
                   '4': button_4_UP, '5': button_5_UP, '6': button_6_UP,
                   '7': button_7_UP, '8': button_8_UP, '9': button_9_UP,
                   '0': button_0_UP}


        for user_parameter in filtered_user_parameters_to_set:
            up_index = f'//*[@id="data"]/table/tbody/tr[{int(user_parameter) + 1}]/td[3]'
            element_input = driver.find_element(By.XPATH, up_index)
            action = ActionChains(driver)
            action.double_click(element_input)
            action.perform()
            time.sleep(self.short_pause)
            # Клик в 1
            for number in filtered_user_parameters_to_set.get(user_parameter):
                driver.find_element(By.XPATH, buttons.get(number)).click()
            time.sleep(self.short_pause)
            # Клик в OK
            element_input = driver.find_element(By.XPATH, button_OK_UP)
            element_input.click()
            time.sleep(self.middle_pause)

    def _get_status_from_web(self, driver, expected_state_for_greenroad):
        pause = 1
        attempts = 10

        driver.switch_to.parent_frame()
        driver.switch_to.frame('content_frame')
        time.sleep(self.short_pause)

        if 'MAN' in expected_state_for_greenroad:
            print(f'expected_stage_for_greenroad: {expected_state_for_greenroad}')
            for attempt in range(attempts):
                elements = driver.find_elements(By.TAG_NAME, 'table')
                curr_state = elements[-1].text
                if '(Фаза)' in curr_state:
                    # curr_stage = elements[-1].text.split('(Фаза) ')[1].replace(' ', '')
                    curr_state = elements[-1].text.split('(Фаза) ')[1]
                    # print(f'curr_stage: {curr_stage}')
                else:
                    print([el.text for el in elements])
                    curr_state = None

                print(f'curr_stage >> {curr_state}')
                print(f'expected_state_for_greenroad >> {expected_state_for_greenroad}')
                if curr_state == expected_state_for_greenroad:
                    print('в if curr_stage == expected_state_for_greenroad ')
                    return curr_state
        elif 'СБРОС' in expected_state_for_greenroad:
            for attempt in range(attempts):
                elements = driver.find_elements(By.TAG_NAME, 'table')
                curr_state = elements[-1].text
                if '(Фаза)' in curr_state:
                    curr_state = elements[-1].text.split('(Фаза) ')[1]
                else:
                    print([el.text for el in elements])
                    curr_state = None

                if 'MAN' not in curr_state:
                    print('в elif СБРОС in expected_state_for_greenroad ')
                    return curr_state


            time.sleep(pause)

    def _get_info_from_web(self, driver):
        pause = 1
        attempts = 10

        driver.switch_to.parent_frame()
        driver.switch_to.frame('content_frame')
        time.sleep(self.short_pause)

        for attempt in range(attempts):
            elements = driver.find_elements(By.TAG_NAME, 'table')
            curr_state = elements[-1].text
            print(f'ecurr_state: {curr_state}')



    def work_ver_reserved_session(self, inputs=None, user_parameters=None, resetting_the_desired_values=None, **kwargs):

        if sdp_func_lib.check_host_tcp(self.ip_adress) == False:
            print('хост недоступен')
            return

        flag_user_inputs, flag_user_parameters = PeekWeb._check_options_for_session(inputs, user_parameters, kwargs)

        print(f'flag_user_inputs: {flag_user_inputs}, flag_user_parameters: {flag_user_parameters}')
        print(f'kwargs: {kwargs}')




        ##############################################################
        span_refresh_change = '//*[@id="refresh_button"]'
        span_start = '//*[@id="mainnav"]/li[1]/a'

        actuator_values = {
            'ВФ': '//*[@id="button_div"]/ul/li[1]/button',
            'ВЫКЛ': '//*[@id="button_div"]/ul/li[2]/button',
            'ВКЛ': '//*[@id="button_div"]/ul/li[3]/button'
        }

        allowed_inputs = ('MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
                          'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
                          'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
                          'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO')
        ##############################################################

        # short_pause = 0.5
        # middle_pause = 1
        long_pause = 4

        driver = webdriver.Chrome()
        try:
            driver.get('http://' + self.ip_adress)
            span_inputs, span_user_parameters = self._start_and_login(driver)

            if flag_user_inputs:

                filtered_inputs_to_set = PeekWeb._make_dict_with_filtered_inputs_and_values(inputs, kwargs)

                time.sleep(self.short_pause)
                print('flag_user_inputs')
                # Клик в Вводы
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
                element_input = driver.find_element(By.XPATH, span_inputs)
                element_input.click()
                time.sleep(self.middle_pause)
                # Клик в Вводы
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                print('1')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
                element_input = driver.find_element(By.XPATH, span_inputs)
                element_input.click()
                print('2')
                time.sleep(self.middle_pause)
                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                time.sleep(self.short_pause)
                driver.switch_to.frame('inst_frame')
                time.sleep(self.short_pause)
                print('3')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_refresh_change)))
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                time.sleep(self.middle_pause)
                driver.switch_to.parent_frame()
                print('4')
                time.sleep(self.middle_pause)

                driver.switch_to.frame('content_frame')
                time.sleep(self.short_pause)

                element = driver.find_element(By.TAG_NAME, 'table')
                element = element.find_elements(By.TAG_NAME, 'tr')

                inputs_to_reset = []
                inputs_from_web = {}

                # Раскакуем переданный словарь, в котором ключ - значение которое будем устанавливать для сброса
                # MPP, а значение - кортеж текущих значений, которые надо скинуть
                if resetting_the_desired_values is not None:
                    (act_val_to_reset, required_actuator_values), = resetting_the_desired_values.items()
                    act_val_to_reset = actuator_values.get(act_val_to_reset)
                else:
                    required_actuator_values = act_val_to_reset = None

                # Сформируем словарь inputs_from_web, где ключом будет название Входа, а значением его №
                # Если в функию передали reset_act_mpp, то параллельно с inputs_from_web сформируем список, в который
                # будем складывать Ввод, у которого значение из required_actuator_values(кортеж из переданного в функцию
                # словаря)
                if resetting_the_desired_values is not None:
                    for el in element:
                        num, name, state, time_state, actuator_val = el.text.split()
                        if name != 'Вход':
                            inputs_from_web[name] = num
                        # Если значение MPP из переданного значения(которое является кортежем) словаря, то кладём Ввод в
                        # inputs_to_reset, чтобы потом в цикле сбросить значения на то, которое является ключом переданного
                        # словаря reset_act_mpp(ВФ или ВЫКЛ)
                        if 'MPP' in name and actuator_val in required_actuator_values:
                            inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')
                else:
                    for el in element:
                        num, name = el.text.split()[0:2]
                        if name != 'Вход':
                            inputs_from_web[name] = num
                # Если есть вводы, требующие сброса, вызываем метод _click_to_mpp_inputs, который это делает
                if inputs_to_reset:
                    print('в inputs_to_reset')
                    self._click_to_mpp_inputs(driver, inputs_to_reset, act_val_to_reset)

                # Циклом обходим отфильтрованный словарь filtered_inputs_to_set, где его ключу(номеру входа) применяем
                # действие, соответствующее значению этого самого ключа(ВКЛ, ВЫКЛ, ВФ)
                flag_set_reset_AUTO = False
                for inp in filtered_inputs_to_set:
                    # Проверяем, если какой нибудь из 'CP_OFF', 'CP_FLASH', 'CP_RED' в filtered_inputs_to_set. Если есть,
                    # то ставим flag_set_reset_AUTO в True(чтобы далее вызвать метод активации и сброса CP_AUTO.
                    # Проверям до первого нахождения. Если нашли, то больше не проверяем, чтобы он не сбросился в след итерации
                    if not flag_set_reset_AUTO:
                        if inp in allowed_inputs[16:19] and filtered_inputs_to_set.get(inp) == 'ВФ':
                            flag_set_reset_AUTO = True
                    num_input = inputs_from_web.get(inp)
                    # Двойной клик в нужный вход в колонке АКТУАТОР:
                    element_input = driver.find_element(By.XPATH,
                                                        f'//*[@id="data"]/table/tbody/tr[{num_input}]/td[5]')
                    action = ActionChains(driver)
                    action.double_click(element_input)
                    action.perform()
                    time.sleep(self.short_pause)
                    # Клик в АКТУАТОР(ВКЛ/ВЫКЛ/ВФ)
                    actuator_value = actuator_values.get(filtered_inputs_to_set.get(inp))
                    element_input = driver.find_element(By.XPATH, actuator_value)
                    element_input.click()
                    time.sleep(self.short_pause)

                if flag_set_reset_AUTO:
                    self._set_reset_cp_auto(driver, inputs_from_web)


                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                driver.switch_to.frame('inst_frame')
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                time.sleep(self.middle_pause)
                # Клик в Старт
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                element_input = driver.find_element(By.XPATH, span_start)
                element_input.click()
                time.sleep(self.long_pause)

                print(f'inputs_from_web: {inputs_from_web}')
                print('Всё ОК')

            elif resetting_the_desired_values is not None:
                print('resetting_the_desired_values is not None')
                # Клик в Вводы
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                print('1')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
                element_input = driver.find_element(By.XPATH, span_inputs)
                element_input.click()
                print('2')
                time.sleep(self.middle_pause)
                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                time.sleep(self.short_pause)
                driver.switch_to.frame('inst_frame')
                time.sleep(self.short_pause)
                print('3')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_refresh_change)))
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                time.sleep(self.middle_pause)
                driver.switch_to.parent_frame()
                print('4')
                time.sleep(self.middle_pause)

                driver.switch_to.frame('content_frame')
                time.sleep(self.short_pause)

                element = driver.find_element(By.TAG_NAME, 'table')
                element = element.find_elements(By.TAG_NAME, 'tr')

                # Собираем в список ВВОДЫ, которые надо скинуть(которые ВКЛ или ВЫКЛ)
                inputs_to_reset = []
                (act_val_to_reset, required_actuator_values), = resetting_the_desired_values.items()
                for el in element:
                    num, name, state, time_state, actuator_val = el.text.split()
                    if 'MPP' in name and actuator_val in required_actuator_values:
                        inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')
                        time.sleep(self.middle_pause)
                print(inputs_to_reset)
                if inputs_to_reset:
                    actuator_val_to_reset = actuator_values.get(act_val_to_reset)
                    self._click_to_mpp_inputs(driver, inputs_to_reset, actuator_val_to_reset)

                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                driver.switch_to.frame('inst_frame')
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                time.sleep(self.middle_pause)
                # Клик в Старт
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                element_input = driver.find_element(By.XPATH, span_start)
                element_input.click()
                time.sleep(self.long_pause)





            if flag_user_parameters:
                print('в if flag_user_parameters')
                # button_1_UP = '//*[@id="buttonpad"]/ul[1]/li[1]/button'
                # button_2_UP = '//*[@id="buttonpad"]/ul[1]/li[2]/button'
                # button_3_UP = '//*[@id="buttonpad"]/ul[1]/li[3]/button'
                # button_4_UP = '//*[@id="buttonpad"]/ul[2]/li[1]/button'
                # button_5_UP = '//*[@id="buttonpad"]/ul[2]/li[2]/button'
                # button_6_UP = '//*[@id="buttonpad"]/ul[2]/li[3]/button'
                # button_7_UP = '//*[@id="buttonpad"]/ul[3]/li[1]/button'
                # button_8_UP = '//*[@id="buttonpad"]/ul[3]/li[2]/button'
                # button_9_UP = '//*[@id="buttonpad"]/ul[3]/li[3]/button'
                # button_0_UP = '//*[@id="buttonpad"]/ul[4]/li[1]/button'
                # button_OK_UP = '//*[@id="buttonpad"]/ul[4]/li[4]/button'
                #
                # buttons = {'1': button_1_UP, '2': button_2_UP, '3': button_3_UP,
                #            '4': button_4_UP, '5': button_5_UP, '6': button_6_UP,
                #            '7': button_7_UP, '8': button_8_UP, '9': button_9_UP,
                #            '0': button_0_UP}

                filtered_user_parameters_to_set = PeekWeb._make_dict_with_filtered_up_and_up_values(user_parameters,
                                                                                                    kwargs)
                time.sleep(self.short_pause)

                # Клик в Параметры программы
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                element_input = driver.find_element(By.XPATH, span_user_parameters)
                element_input.click()
                time.sleep(1)
                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                driver.switch_to.frame('inst_frame')
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                time.sleep(1)
                driver.switch_to.parent_frame()
                driver.switch_to.frame('content_frame')

                # Установка переданных UP
                print(filtered_user_parameters_to_set)
                # for user_parameter in filtered_user_parameters_to_set:
                #     up_index = f'//*[@id="data"]/table/tbody/tr[{int(user_parameter) + 1}]/td[3]'
                #     element_input = driver.find_element(By.XPATH, up_index)
                #     action = ActionChains(driver)
                #     action.double_click(element_input)
                #     action.perform()
                #     # time.sleep(1)
                #     # Клик в 1
                #     for number in filtered_user_parameters_to_set.get(user_parameter):
                #         driver.find_element(By.XPATH, buttons.get(number)).click()
                #     # Клик в OK
                #     element_input = driver.find_element(By.XPATH, button_OK_UP)
                #     element_input.click()
                #     time.sleep(1)
                self._click_to_up_and_val_up(driver, filtered_user_parameters_to_set)
                # Клик в Обновить/изменить
                driver.switch_to.parent_frame()
                driver.switch_to.frame('inst_frame')
                element_input = driver.find_element(By.XPATH, span_refresh_change)
                element_input.click()
                # Клик в Старт
                driver.switch_to.parent_frame()
                driver.switch_to.frame('menu_frame')
                element_input = driver.find_element(By.XPATH, span_start)
                element_input.click()
                time.sleep(self.middle_pause)

            time.sleep(self.long_pause)
        except Exception as ex:
            print('ЭКСЭПТНУЛСЯ')
            with open(configuration.path_to_faults_log_webdriver, 'w') as erlog:
                erlog.write(f"{ex}"
                            f"Время ошибки: {datetime.datetime.now()}\n\n")
                if 'ERR_CONNECTION_TIMED_OUT' in str(ex):
                    pass

    def session_refactor(self, increase_the_timeout=False,
                         session_for_greenroad=False, expected_state_for_greenroad=None,
                         inputs=None, user_parameters=None, resetting_the_desired_values=None, **kwargs):
        """ Метод создаёт web сессию, в которрй совершаются действия в зависимости от переданных аргументов:
        :param bool increase_the_timeout: увеличивает таймаут с каждым новым вызовом метода у экземпляра
        :param bool session_for_greenroad: если метод вызван для "Зелёной улицы" приложения Engineering_tool_kit,
               то при наличии :arg: resetting_the_desired_values - не будет сбрасывать MPP_MAN
        :param dict inputs: словарь "Вводов", которые необходимо актировать. Ключ словаря - название Ввода, значение -
               значение Актутора, которое необходимо установить
        :param dict user_parameters: словарь "параметров программы", которые необходимо установить.
               Ключ словаря - str, которая должна содердать ращзделитель "_". Всё, что до "_" -> произольно. После
               "_" -> индекс параметра. Например: UP_2, UP->произвольная часть, 2->индекс параметра.
               Значение словаря - str/int -> значение, которе будет утсановлено в поле "Значение".
               Например: UP_2: 154 -> установить значение 154 для юзер параметра с индексом 2
        :param dict resetting_the_desired_values: ключ - str Актуатор(ВФ, ВЫКЛ, ВКЛ), который будет установлен для
               Вводов, текущее значение которых содержится в tuple значении словаря.
               Например: {'ВЫКЛ: (ВКЛ, )'} - это значит ВЫКЛ будет установлено для всех Вводов, текущее сотсояние
               которых 'ВКЛ'
               Еще пример: {'ВФ: (ВКЛ, ВЫКЛ)'} - это значит ВФ будет установлено для всех Вводов, текущее сотсояние
               которых 'ВКЛ' или 'ВЫКЛ'
        :param kwargs: можно передавать Вводы или параметры программы вместо ipputs/user_parameters.
               Например: MPP_MAN=ВКЛ, MPP_PH1=ВЫКЛ, CP_RED=ВКЛ, UP_1=154, UP_3=1 и т.д.
        :param expected_state_for_greenroad: фаза, которую необходимо включить из Engineering_tool_kit_v1.0 "greenroad"
        """


        filtered_inputs_to_set = None
        # print(f'increase_the_timeout: {increase_the_timeout}')
        if increase_the_timeout:
            self.short_pause += 1
            self.middle_pause += 2
            self.long_pause += 2
        # print(f'timeout из session_refactor:')
        # print(f'self.short_pause >> {self.short_pause}')
        # print(f'self.middle_pause >> {self.middle_pause}')
        # print(f'self.long_pause >> {self.long_pause}')

        if sdp_func_lib.check_host_tcp(self.ip_adress) == False:
            return

        flag_user_inputs, flag_user_parameters = PeekWeb._check_options_for_session(inputs, user_parameters, kwargs)

        # print(f'flag_user_inputs: {flag_user_inputs}, flag_user_parameters: {flag_user_parameters}')
        # print(f'kwargs: {kwargs}')

        ##############################################################
        span_refresh_change = '//*[@id="refresh_button"]'
        span_start = '//*[@id="mainnav"]/li[1]/a'

        actuator_values = {
            'ВФ': '//*[@id="button_div"]/ul/li[1]/button',
            'ВЫКЛ': '//*[@id="button_div"]/ul/li[2]/button',
            'ВКЛ': '//*[@id="button_div"]/ul/li[3]/button'
        }

        allowed_inputs = ('MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
                          'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
                          'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
                          'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO')
        ##############################################################

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')


        driver = webdriver.Chrome(options=options)

        driver.get('http://' + self.ip_adress)
        span_inputs, span_user_parameters = self._start_and_login(driver)

        # Если в аргументы переданы какие нибудь из Вводов
        if flag_user_inputs:

            filtered_inputs_to_set = PeekWeb._make_dict_with_filtered_inputs_and_values(inputs, kwargs)

            time.sleep(self.short_pause)
            # print('flag_user_inputs')
            # Клик в Вводы
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
            element_input = driver.find_element(By.XPATH, span_inputs)
            element_input.click()
            time.sleep(self.middle_pause)
            # Клик в Вводы
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            # print('1')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
            element_input = driver.find_element(By.XPATH, span_inputs)
            element_input.click()
            # print('2')
            time.sleep(self.middle_pause)
            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            time.sleep(self.short_pause)
            driver.switch_to.frame('inst_frame')
            time.sleep(self.short_pause)
            # print('3')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_refresh_change)))
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            time.sleep(self.middle_pause)
            driver.switch_to.parent_frame()
            # print('4')
            time.sleep(self.middle_pause)

            driver.switch_to.frame('content_frame')
            time.sleep(self.short_pause)

            element = driver.find_element(By.TAG_NAME, 'table')
            element = element.find_elements(By.TAG_NAME, 'tr')

            inputs_to_reset = []
            inputs_from_web = {}

            # Раскакуем переданный словарь, в котором ключ - значение которое будем устанавливать для сброса
            # MPP, а значение - кортеж текущих значений, которые надо скинуть
            if resetting_the_desired_values is not None:
                (act_val_to_reset, required_actuator_values), = resetting_the_desired_values.items()
                act_val_to_reset = actuator_values.get(act_val_to_reset)
            else:
                required_actuator_values = act_val_to_reset = None

            # Сформируем словарь inputs_from_web, где ключом будет название Входа, а значением его №
            # Если в функию передали reset_act_mpp, то параллельно с inputs_from_web сформируем список, в который
            # будем складывать Ввод, у которого значение из required_actuator_values(кортеж из переданного в функцию
            # словаря)
            if resetting_the_desired_values is not None:
                for el in element:
                    num, name, state, time_state, actuator_val = el.text.split()
                    # print(f'num: {num}, name: {name},state: {state},time_state: {time_state},actuator_val: {actuator_val}')
                    if name != 'Вход':
                        inputs_from_web[name] = num
                    # Если значение MPP из переданного значения(которое является кортежем) словаря, то кладём Ввод в
                    # inputs_to_reset, чтобы потом в цикле сбросить значения на то, которое является ключом переданного
                    # словаря reset_act_mpp(ВФ или ВЫКЛ)
                    if 'MPP' in name and actuator_val in required_actuator_values and not session_for_greenroad:
                        inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')
                    # elif 'MPP' in name and actuator_val in required_actuator_values and \
                    #         session_for_greeroad and name + actuator_val != 'MPP_MANВКЛ':
                    #     inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')
                        # print(f'name + actuator_val{name}{actuator_val}')
                    elif PeekWeb._check_mpp_for_reset(name, state, actuator_val,
                                                      required_actuator_values, session_for_greenroad):
                        print('после нужного elif')
                        inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')

            else:
                for el in element:
                    num, name = el.text.split()[0:2]
                    if name != 'Вход':
                        inputs_from_web[name] = num
            # Если есть вводы, требующие сброса, вызываем метод _click_to_mpp_inputs, который это делает
            if inputs_to_reset:
                # print('в inputs_to_reset')
                self._click_to_mpp_inputs(driver, inputs_to_reset, act_val_to_reset)

            # Циклом обходим отфильтрованный словарь filtered_inputs_to_set, где его ключу(номеру входа) применяем
            # действие, соответствующее значению этого самого ключа(ВКЛ, ВЫКЛ, ВФ)
            flag_set_reset_AUTO = False
            for inp in filtered_inputs_to_set:
                # Проверяем, если какой нибудь из 'CP_OFF', 'CP_FLASH', 'CP_RED' в filtered_inputs_to_set. Если есть,
                # то ставим flag_set_reset_AUTO в True(чтобы далее вызвать метод активации и сброса CP_AUTO.
                # Проверям до первого нахождения. Если нашли, то больше не проверяем, чтобы он не сбросился в след итерации
                if not flag_set_reset_AUTO:
                    if inp in allowed_inputs[16:19] and filtered_inputs_to_set.get(inp) == 'ВФ':
                        flag_set_reset_AUTO = True
                num_input = inputs_from_web.get(inp)
                # Двойной клик в нужный вход в колонке АКТУАТОР:
                element_input = driver.find_element(By.XPATH,
                                                    f'//*[@id="data"]/table/tbody/tr[{num_input}]/td[5]')
                action = ActionChains(driver)
                action.double_click(element_input)
                action.perform()
                time.sleep(self.short_pause)
                # Клик в АКТУАТОР(ВКЛ/ВЫКЛ/ВФ)
                actuator_value = actuator_values.get(filtered_inputs_to_set.get(inp))
                element_input = driver.find_element(By.XPATH, actuator_value)
                element_input.click()
                time.sleep(self.short_pause)

            if flag_set_reset_AUTO:
                self._set_reset_cp_auto(driver, inputs_from_web)

            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            driver.switch_to.frame('inst_frame')
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            time.sleep(self.middle_pause)
            # Клик в Старт
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            element_input = driver.find_element(By.XPATH, span_start)
            element_input.click()
            time.sleep(self.long_pause)

            # print(f'inputs_from_web: {inputs_from_web}')
            # print('Всё ОК')
        # Если в аргументы передан только сброс Вводов
        elif resetting_the_desired_values is not None:
            # print('resetting_the_desired_values is not None')
            # Клик в Вводы
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            # print('1')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_inputs)))
            element_input = driver.find_element(By.XPATH, span_inputs)
            element_input.click()
            # print('2')
            time.sleep(self.middle_pause)
            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            time.sleep(self.short_pause)
            driver.switch_to.frame('inst_frame')
            time.sleep(self.short_pause)
            # print('3')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, span_refresh_change)))
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            time.sleep(self.middle_pause)
            driver.switch_to.parent_frame()
            # print('4')
            time.sleep(self.middle_pause)

            driver.switch_to.frame('content_frame')
            time.sleep(self.short_pause)

            element = driver.find_element(By.TAG_NAME, 'table')
            element = element.find_elements(By.TAG_NAME, 'tr')

            # Собираем в список ВВОДЫ, которые надо скинуть(которые ВКЛ или ВЫКЛ)
            inputs_to_reset = []
            (act_val_to_reset, required_actuator_values), = resetting_the_desired_values.items()
            for el in element:
                num, name, state, time_state, actuator_val = el.text.split()
                if 'MPP' in name and actuator_val in required_actuator_values:
                    inputs_to_reset.append(f'//*[@id="data"]/table/tbody/tr[{num}]/td[5]')
                    time.sleep(self.middle_pause)
            # print(inputs_to_reset)
            if inputs_to_reset:
                actuator_val_to_reset = actuator_values.get(act_val_to_reset)
                self._click_to_mpp_inputs(driver, inputs_to_reset, actuator_val_to_reset)

            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            driver.switch_to.frame('inst_frame')
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            time.sleep(self.middle_pause)
            # Клик в Старт
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            element_input = driver.find_element(By.XPATH, span_start)
            element_input.click()
            time.sleep(self.long_pause)
        # Если в аргументы переданы какие параметров программы(юзер-параметры)
        if flag_user_parameters:
            # print('в if flag_user_parameters')

            filtered_user_parameters_to_set = PeekWeb._make_dict_with_filtered_up_and_up_values(user_parameters,
                                                                                                kwargs)
            time.sleep(self.short_pause)

            # Клик в Параметры программы
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            element_input = driver.find_element(By.XPATH, span_user_parameters)
            element_input.click()
            time.sleep(1)
            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            driver.switch_to.frame('inst_frame')
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            time.sleep(1)
            driver.switch_to.parent_frame()
            driver.switch_to.frame('content_frame')

            # Установка переданных UP
            # print(filtered_user_parameters_to_set)

            self._click_to_up_and_val_up(driver, filtered_user_parameters_to_set)
            # Клик в Обновить/изменить
            driver.switch_to.parent_frame()
            driver.switch_to.frame('inst_frame')
            element_input = driver.find_element(By.XPATH, span_refresh_change)
            element_input.click()
            # Клик в Старт
            driver.switch_to.parent_frame()
            driver.switch_to.frame('menu_frame')
            element_input = driver.find_element(By.XPATH, span_start)
            element_input.click()
            time.sleep(self.middle_pause)

            self._get_info_from_web(driver)



        time.sleep(self.middle_pause)
        if session_for_greenroad or expected_state_for_greenroad is not None:
            result_session = self._get_status_from_web(driver, expected_state_for_greenroad)
        else:
            result_session = 'the session was completed successfully'

        time.sleep(self.long_pause)
        print('-----End-------')
        driver.close()
        return result_session



        # element = element.find_elements(By.TAG_NAME, 'tr')








class PotokWeb:
    def __init__(self, ip_adress, flag=None):
        self.ip_adress = ip_adress

        if flag == 'reboot':
            self.restart_controller_potok_webdriver()

    def restart_controller_potok_webdriver(self):

        if not sdp_func_lib.check_host_tcp(self.ip_adress):
            return

        driver = webdriver.Chrome()

        try:
            # Открыть браузер Chrome
            driver.get(f'https://{self.ip_adress}')

            button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
            link_go_to_site = '//*[@id="proceed-link"]'
            login = '//*[@id="login"]'
            password = '//*[@id="password"]'
            button_login = '/html/body/div[2]/div/div/form/button'
            # button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
            # radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
            # radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
            # button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

            time.sleep(1)
            # Клик в "Дополнительно"(небезопасый сайт)
            element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
            element_input.click()
            time.sleep(1)
            # Клик в перейти на сайт
            element_input = driver.find_element(By.XPATH, link_go_to_site)
            element_input.click()
            time.sleep(1)
            # Ввод логина и пароля
            element_input = driver.find_element(By.XPATH, login)
            element_input.send_keys('admin')
            element_input = driver.find_element(By.XPATH, password)
            element_input.send_keys('zBCTRuV7')
            # Клик на кнопку Войти
            element_input = driver.find_element(By.XPATH, button_login)
            element_input.click()
            time.sleep(1)

            driver.get(f'https://{self.ip_adress}/system_reboot')
        except:
            pass

        #     # Клик на кнопку Перезапуск программы
        #     if action == "Перезапуск программы":
        #         element_input = driver.find_element(By.XPATH, button_restart_programm)
        #         element_input.click()
        #         keyboard.send("enter")
        #     # Клик на radiobutton Фиксированный:
        #     elif action == "Фикс":
        #         element_input = driver.find_element(By.XPATH, radio_button_fix)
        #         element_input.click()
        #         time.sleep(1)
        #         element_input = driver.find_element(By.XPATH, button_change_mode)
        #         element_input.click()
        #     # Клик на radiobutton Адаптивный:
        #     elif action == "Адаптива":
        #         element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
        #         element_input.click()
        #         time.sleep(1)
        #         element_input = driver.find_element(By.XPATH, button_change_mode)
        #         element_input.click()
        #     # Перезапуск ОС контроллера:
        #     elif action == "Перезапуск ОС":
        #         driver.get('https://' + ip_adress + '/system_reboot')
        #
        #
        #     time.sleep(4)
        #
        # except Exception as ex:
        #     pass
        # finally:
        #     # driver.close()
        #     driver.quit()


def restart_programm_potok_webdriver(ip_adress: str, action: str):

    if not sdp_func_lib.check_host_tcp(ip_adress):
        return

    driver = webdriver.Chrome()

    try:
        # Открыть браузер Chrome
        driver.get('https://' + ip_adress)

        button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
        link_go_to_site = '//*[@id="proceed-link"]'
        login = '//*[@id="login"]'
        password = '//*[@id="password"]'
        button_login = '/html/body/div[2]/div/div/form/button'
        button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
        radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
        radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
        button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

        time.sleep(1)
        # Клик в "Дополнительно"(небезопасый сайт)
        element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
        element_input.click()
        time.sleep(1)
        # Клик в перейти на сайт
        element_input = driver.find_element(By.XPATH, link_go_to_site)
        element_input.click()
        time.sleep(1)
        # Ввод логина и пароля
        element_input = driver.find_element(By.XPATH, login)
        element_input.send_keys('admin')
        element_input = driver.find_element(By.XPATH, password)
        element_input.send_keys('zBCTRuV7')
        # Клик на кнопку Войти
        element_input = driver.find_element(By.XPATH, button_login)
        element_input.click()
        time.sleep(1)

        # Клик на кнопку Перезапуск программы
        if action == "Перезапуск программы":
            element_input = driver.find_element(By.XPATH, button_restart_programm)
            element_input.click()
            keyboard.send("enter")
        # Клик на radiobutton Фиксированный:
        elif action == "Фикс":
            element_input = driver.find_element(By.XPATH, radio_button_fix)
            element_input.click()
            time.sleep(1)
            element_input = driver.find_element(By.XPATH, button_change_mode)
            element_input.click()
        # Клик на radiobutton Адаптивный:
        elif action == "Адаптива":
            element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
            element_input.click()
            time.sleep(1)
            element_input = driver.find_element(By.XPATH, button_change_mode)
            element_input.click()
        # Перезапуск ОС контроллера:
        elif action == "Перезапуск ОС":
            driver.get('https://' + ip_adress + '/system_reboot')


        time.sleep(4)

    except Exception as ex:
        pass
    finally:
        # driver.close()
        driver.quit()


def restart_controller_potok_webdriver(ip_adress: str):

    if not sdp_func_lib.check_host_tcp(ip_adress):
        return

    driver = webdriver.Chrome()

    try:
        # Открыть браузер Chrome
        driver.get(f'https://{ip_adress}')

        button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
        link_go_to_site = '//*[@id="proceed-link"]'
        login = '//*[@id="login"]'
        password = '//*[@id="password"]'
        button_login = '/html/body/div[2]/div/div/form/button'
        # button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
        # radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
        # radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
        # button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

        time.sleep(1)
        # Клик в "Дополнительно"(небезопасый сайт)
        element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
        element_input.click()
        time.sleep(1)
        # Клик в перейти на сайт
        element_input = driver.find_element(By.XPATH, link_go_to_site)
        element_input.click()
        time.sleep(1)
        # Ввод логина и пароля
        element_input = driver.find_element(By.XPATH, login)
        element_input.send_keys('admin')
        element_input = driver.find_element(By.XPATH, password)
        element_input.send_keys('zBCTRuV7')
        # Клик на кнопку Войти
        element_input = driver.find_element(By.XPATH, button_login)
        element_input.click()
        time.sleep(1)

        driver.get(f'https://{ip_adress}/system_reboot')
    except:
        pass

    #     # Клик на кнопку Перезапуск программы
    #     if action == "Перезапуск программы":
    #         element_input = driver.find_element(By.XPATH, button_restart_programm)
    #         element_input.click()
    #         keyboard.send("enter")
    #     # Клик на radiobutton Фиксированный:
    #     elif action == "Фикс":
    #         element_input = driver.find_element(By.XPATH, radio_button_fix)
    #         element_input.click()
    #         time.sleep(1)
    #         element_input = driver.find_element(By.XPATH, button_change_mode)
    #         element_input.click()
    #     # Клик на radiobutton Адаптивный:
    #     elif action == "Адаптива":
    #         element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
    #         element_input.click()
    #         time.sleep(1)
    #         element_input = driver.find_element(By.XPATH, button_change_mode)
    #         element_input.click()
    #     # Перезапуск ОС контроллера:
    #     elif action == "Перезапуск ОС":
    #         driver.get('https://' + ip_adress + '/system_reboot')
    #
    #
    #     time.sleep(4)
    #
    # except Exception as ex:
    #     pass
    # finally:
    #     # driver.close()
    #     driver.quit()
