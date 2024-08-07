import asyncio
import os
import socket
import subprocess
import sys
import time

import aiohttp

import requests

from pysnmp.hlapi.asyncio import *

protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')

""" Oids Swarco """
swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
swarcoUTCCommandDark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
swarcoUTCCommandFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
swarcoUTCTrafftechPlanCommand = '1.3.6.1.4.1.1618.3.7.2.2.1.0'
swarcoUTCStatusEquipment = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
swarcoUTCTrafftechPlanCurrent = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
swarcoUTCTrafftechPlanSource = '.1.3.6.1.4.1.1618.3.7.2.1.3'
swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'
swarcoUTCDetectorQty = '1.3.6.1.4.1.1618.3.3.2.2.2.0'
get_val_stage_STCIP_swarco = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '1': 8}
# Ключи значения фаз для set запросов STCIP Swarco
set_stage_STCIP_swarco_values = {'1': '2', '2': '3', '3': '4', '4': '5',
                                 '5': '6', '6': '7', '7': '8', '8': '1',
                                 'ЛОКАЛ': '0'}
""" Oids Potok-S """
potokS_rw_Dark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
potokS_rw_YellowFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
potokS_rw_Red = '1.3.6.1.4.1.1618.3.2.2.4.1.0'
potokS_rw_StageCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
potokS_r_Mode = '1.3.6.1.4.1.1618.3.6.2.2.2.0'
potokS_r_ControlState = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
potokS_r_PlanSource = '.1.3.6.1.4.1.1618.3.7.2.1.3.0'
potokS_r_PlanStatus = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
potokS_r_StageStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
potokS_w_RestartProgramm = '.1.3.6.1.4.1.1618.3.2.2.3.1.0'
###########################################################
get_val_stage_STCIP_potok = {
    str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))
}
set_stage_STCIP_potok_values = {
    str(k) if k < 65 else 'ЛОКАЛ': str(v) if k < 65 else '0' for k, v in zip(range(1, 68), range(2, 69))
}
""" Oids Potok-P """
potok_w_DarkCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.11'
potok_w_FlashCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.20'
potok_rw_StageCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.5'
potok_rw_AllowBitTO = '.1.3.6.1.4.1.13267.3.2.4.2.1.15'
potok_r_ManPanel_Status = '1.3.6.1.4.1.13267.3.2.5.1.1.15'
potok_rw_OperationMode = '.1.3.6.1.4.1.13267.3.2.4.1.0'
potok_rw_OperationModeTimeout = '.1.3.6.1.4.1.13267.3.2.2.4.0'
potok_r_StageStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.3'
potok_r_PlanStatus = '.1.3.6.1.4.1.13267.1.2.9.1.3'
potok_r_PlanSource = '1.3.6.1.4.1.13267.1.2.9.1.3.1'
potok_r_DarkStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.45'
potok_r_FlashStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.36'
potok_w_restart_programm = '.1.3.6.1.4.1.13267.3.2.4.2.1.5.5'
potok_r_DetError = '1.3.6.1.4.1.13267.3.2.5.1.1.5'
potok_r_ElectricalCircuitErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.3'
potok_r_LocalAdaptiv = '1.3.6.1.4.1.13267.3.2.5.1.1.46'

def val_stages_for_get_stage_UG405_potok(option=None):
    """ В зависимости от опции функция формирует словарь с номером и значением фазы
    """
    # print(f'option: {option}')
    if option == 'get':
        mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
        stages = ['0x01', '0x02', '0x04', '0x08', '0x10', ' ', '@', '0x80']

        # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
        # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
        for i in range(7):
            temp_lst = [
                f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
            ]
            stages = stages + temp_lst
        # print(stages)

        get_val_stage_UG405_POTOK = {k: v for v, k in enumerate(stages, 1)}
        return get_val_stage_UG405_POTOK
        # print(get_val_stage_UG405_POTOK)
    elif option == 'set':
        mask_after_8stages_set = ['0x01', '0x02', '0x04', '0x08', '0x10', '0x20', '0x40', '0x80']
        stages = ['0x01', '0x02', '0x04', '0x08', '0x10', '0x20', '0x40', '0x80']
        for i in range(7):
            temp_lst = [
                f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
            ]
            stages = stages + temp_lst
        set_val_stage_UG405_POTOK = {str(k): v for k, v in enumerate(stages, 1)}
        # print(set_val_stage_UG405_POTOK)
        return set_val_stage_UG405_POTOK

# Значения фаз для для UG405 Potok
get_val_stage_UG405_POTOK = val_stages_for_get_stage_UG405_potok(option='get')
set_stage_UG405_potok_values = val_stages_for_get_stage_UG405_potok(option='set')
""" **************PEEK**************** """
# Oid
peek_utcType2OperationModeTimeout = '.1.3.6.1.4.1.13267.3.2.2.4.0'
peek_utcType2OperationMode = '.1.3.6.1.4.1.13267.3.2.4.1.0'
peek_utcControlLO = '.1.3.6.1.4.1.13267.3.2.4.2.1.11'
peek_utcControlFF = '.1.3.6.1.4.1.13267.3.2.4.2.1.20'
peek_utcControlTO = '.1.3.6.1.4.1.13267.3.2.4.2.1.15'
peek_utcControlFn = '.1.3.6.1.4.1.13267.3.2.4.2.1.5'
peek_utcReplyGn = '.1.3.6.1.4.1.13267.3.2.5.1.1.3'
##########################################################
def val_stages_for_get_stage_UG405_peek(option=None):
    """ В зависимости от опции функция формирует словарь с номером и значением фазы
    """
    # print(f'option: {option}')
    if option == 'get':
        mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
        stages = ['01', '02', '04', '08', '10', '6', '@', '80']

        # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
        # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
        for i in range(7):
            temp_lst = [
                f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
            ]
            stages = stages + temp_lst
        # print(stages)

        get_val_stage_UG405_Peek = {k: v for v, k in enumerate(stages, 1)}
        return get_val_stage_UG405_Peek
        # print(get_val_stage_UG405_POTOK)
    elif option == 'set':
        mask_after_8stages_set = ['01', '02', '04', '08', '10', '20', '40', '80']
        stages = ['01', '02', '04', '08', '10', '20', '40', '80']
        for i in range(7):
            temp_lst = [
                f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
            ]
            stages = stages + temp_lst
        set_val_stage_UG405_Peek = {str(k): v for k, v in enumerate(stages, 1)}
        # print(set_val_stage_UG405_POTOK)
        return set_val_stage_UG405_Peek

# Ключи значения фаз для get запросов UG405 Peek
get_val_stage_UG405_PEEK = {'0100': 1, '0200': 2, '0400': 3, '0800': 4,
                            '1000': 5, '2000': 6, '4000@': 7, '8000': 8,
                            '0001': 9, '0002': 10, '0004': 11, '0008': 12,
                            '0010': 13, '0020': 14, '0040@': 15, '0080': 16,

                            '010000': 1, '020000': 2, '040000': 3, '080000': 4,
                            '100000': 5, '200000': 6, '400000@': 7, '800000': 8,
                            '000100': 9, '000200': 10, '000400': 11, '000800': 12,
                            '001000': 13, '002000': 14, '004000@': 15, '008000': 16,

                            '01000000': 1, '02000000': 2, '04000000': 3, '08000000': 4,
                            '10000000': 5, '20000000': 6, '40000000@': 7, '80000000': 8,
                            '00010000': 9, '00020000': 10, '00040000': 11, '00080000': 12,
                            '00100000': 13, '00200000': 14, '00400000@': 15, '00800000': 16,

                            '01': 1, '02': 2, '04': 3, '08': 4,
                            '10': 5, '6': 6, '@': 7, '80': 8,
                            }
# Ключи значения фаз для set запросов UG405 Peek
set_stage_UG405_peek_values = val_stages_for_get_stage_UG405_peek(option='set')
# Get status from Web
mask_url_get_data = '/hvi?file=m001a.hvi&pos1=0&pos2=-1'
state_CONTROL = ('УПРАВЛЕНИЕ', 'CONTROL')
state_FLASH = 'МИГАНИЕ'
state_RED = 'КРУГОМ КРАСНЫЙ'
modeVA = 'VA'
modeFT = 'FT'
modeMAN = 'MAN'
modeUTC = 'UTC'
modeCLF = 'CLF'



ip_adress = '10.179.102.161'
community = 'private'

async def get_stage(ip_adress, community, oids):

    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161), timeout=0, retries=0),
        ContextData(),
        *oids
    )
    return varBinds


async def get_data_for_toolkit_snmp(ip_adress: str, community: str, num_host: str, protocol: str,
                                    oids: list, timeout=1, retries=0):

    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
        ContextData(),
        *oids
    )
    return num_host, protocol, varBinds


async def get_data_for_toolkit_http_peek(ip_adress, num_host, timeout=1):

    url = f'http://{ip_adress}/hvi?file=m001a.hvi&pos1=0&pos2=-1'
    timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as s:
                assert s.status == 200
                content = await s.text()
    except aiohttp.client_exceptions.ClientConnectorError as e:
        content = f'Нет соединения с хостом {e}'
    except asyncio.TimeoutError as e:
        content = f'Нет соединения с хостом-> {e}'
    return num_host, protocols[3], content


def convert_scn(scn):
    """ Функция получает на вход строку, которую необходимо конвертировать в SCN
        для управления и мониторинга по протоколу UG405.
        Например: convert_scn(CO1111)
    """
    len_scn = str(len(scn)) + '.'
    convert_to_ASCII = [str(ord(c)) for c in scn]
    scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
    return scn

def create_oids(protocol, scn=None):

    if protocol == protocols[0]:
        scn = convert_scn(scn)

        oids = [ObjectType(ObjectIdentity(potok_r_StageStatus + scn)),
                ObjectType(ObjectIdentity(potok_r_PlanStatus + scn)),
                ObjectType(ObjectIdentity(potok_r_PlanSource + scn)),
                ObjectType(ObjectIdentity(potok_r_DetError + scn)),
                ObjectType(ObjectIdentity(potok_rw_AllowBitTO + scn)),
                ObjectType(ObjectIdentity(potok_r_LocalAdaptiv + scn)),
                ObjectType(ObjectIdentity(potok_r_ManPanel_Status + scn)),
                ObjectType(ObjectIdentity(potok_r_ElectricalCircuitErr + scn)),
                ]
        community = 'UTMC'
    elif protocol == protocols[1]:
        pass
    elif protocol == protocols[2]:
        oids = [ObjectType(ObjectIdentity(swarcoUTCTrafftechPhaseStatus)),
                ObjectType(ObjectIdentity(swarcoUTCTrafftechPlanCurrent)),
                ObjectType(ObjectIdentity(swarcoUTCDetectorQty)),
                ObjectType(ObjectIdentity(swarcoSoftIOStatus)),
                ]
        community = 'private'
    elif protocol == protocols[3]:
        pass
    else:
        return 'Bad protocol'

    return oids, community

def processing_data_toolkit(raw_data):
    statusMode = {
        '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '00': 'Ошибка электрической цепи',
        '--': 'Нет данных',
    }

    processed_data = {}
    for host_data in raw_data:
        if host_data[2]:
            num_host, protocol, varBinds = host_data
            if protocol == protocols[0]:
                stage = get_val_stage_UG405_POTOK.get(varBinds[0][1].prettyPrint())
                # print(f'stage UG = {stage}')
                # print(f'get_val_stage_UG405_POTOK = {get_val_stage_UG405_POTOK}')
                plan = varBinds[1][1].prettyPrint()
                plan_source = varBinds[2][1].prettyPrint()
                det_err = varBinds[3][1].prettyPrint()
                allowBitTO = varBinds[4][1].prettyPrint()
                local_adaptiv = varBinds[5][1].prettyPrint()
                manual = varBinds[6][1].prettyPrint()
                electrics = varBinds[7][1].prettyPrint()
                # operMode = varBinds[5][1].prettyPrint()
                if plan != '0' and plan_source == '1':
                    if det_err == '0' and local_adaptiv == '1':
                        mode = statusMode.get('8')
                    else:
                        mode = statusMode.get('12')
                elif plan == '0' and plan_source == '2' and allowBitTO == '1':
                    mode = statusMode.get('11')
                elif manual == '1':
                    mode = statusMode.get('10')
                elif electrics == '1':
                    mode = statusMode.get('00')
                else:
                    mode = statusMode.get('--')
                processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'

            elif protocol == protocols[1]:
                pass
            elif protocol == protocols[2]:
                stage = get_val_stage_STCIP_swarco.get(varBinds[0][1].prettyPrint())
                plan, num_detlogics, softinp181 = (varBinds[1][1].prettyPrint(), varBinds[2][1].prettyPrint(),
                                                   varBinds[3][1].prettyPrint()[180])
                if plan == '16':
                    mode = statusMode.get('11')
                elif plan == '15':
                    mode = statusMode.get('10')
                elif softinp181 == '1' or num_detlogics == '0':
                    mode = statusMode.get('12')
                elif softinp181 == '0' and num_detlogics.isdigit() and int(num_detlogics) > 2:
                    mode = statusMode.get('8')
                else:
                    mode = statusMode.get('--')
                processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'
            elif protocol == protocols[3]:
                if 'Нет соединения с хостом' in varBinds:
                    processed_data[num_host] = varBinds
                    continue

                state = mode = None
                for line in varBinds.split('\n'):
                    if 'T_PLAN' in line:
                        plan = line.replace(':D;;##T_PLAN##;', '').replace('-', '').replace(' ', '')
                    elif ':SUBTITLE' in line:
                        adress = line.replace(':SUBTITLE;Moscow:', '')
                    elif 'T_STATE' in line:
                        state = line.replace(':D;;##T_STATE##;', '')

                    elif 'T_MODE' in line:
                        mode, stage = line.replace(':D;;##T_MODE## (##T_STAGE##);', '').split()
                        stage = stage.replace('(', '').replace(')', '')
                        break

                if stage.isdigit() and int(stage) > 0 and state.strip() in state_CONTROL:
                    if mode == modeVA:
                        mode = statusMode.get('8')
                    elif mode == modeFT:
                        mode = statusMode.get('12')
                    elif mode == modeMAN:
                        mode = statusMode.get('10')
                    elif mode == modeUTC:
                        mode = statusMode.get('11')
                    else:
                        mode = statusMode.get('--')
                    processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'

            print(f'mode : {mode}')
    return processed_data

# async def main():
#
#     tasks = [get_stage('192.168.1.1', community), get_stage('192.168.1.1', community), get_stage('192.168.1.1', community),
#              get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),
#              get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),
#              get_stage(ip_adress, community,) ,get_stage(ip_adress, community,)]
#     values = await asyncio.gather(*tasks)
#     print(values)
# start_time = time.time()
# res = asyncio.run(main())
# print(f'operation time = {time.time() - start_time}')
#
# print(f'res = {res}')
#
# for oid, val in res:
#     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')
