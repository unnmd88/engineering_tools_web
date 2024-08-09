import asyncio
import os
import socket
import subprocess
import sys
import time

import aiohttp
import requests

from pysnmp.hlapi.asyncio import *

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
        stages = ['01', '02', '04', '08', '10', '6', '@', '80']

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
    print(f'async get_stage для {ip_adress}')
    # oids = (swarcoUTCTrafftechPhaseStatus, swarcoUTCTrafftechPlanCurrent, swarcoSoftIOStatus, swarcoUTCDetectorQty)
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161), timeout=0, retries=0),
        ContextData(),
        *oids
    )
    # for oid, val in varBinds:
    #     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')
    return varBinds


async def get_stage_for_toolkit(ip_adress: str, community: str, num_host: str, protocol: str,
                                oids: list, timeout=1, retries=0):
    print(f'async get_stage для {ip_adress}')
    # oids = (swarcoUTCTrafftechPhaseStatus, swarcoUTCTrafftechPlanCurrent, swarcoSoftIOStatus, swarcoUTCDetectorQty)
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
        ContextData(),
        *oids
    )
    # for oid, val in varBinds:
    #     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')
    return num_host, protocol, varBinds


async def main():

    tasks = [get_stage('192.168.1.1', community), get_stage('192.168.1.1', community), get_stage('192.168.1.1', community),
             get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),
             get_stage('192.168.1.1', community),get_stage('192.168.1.1', community),
             get_stage(ip_adress, community,) ,get_stage(ip_adress, community,)]
    values = await asyncio.gather(*tasks)
    print(values)
start_time = time.time()
res = asyncio.run(main())
print(f'operation time = {time.time() - start_time}')

print(f'res = {res}')

for oid, val in res:
    print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')
