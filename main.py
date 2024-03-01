# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
from piinspy import *
import time
import numpy as np
from utility import *

smu = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2460::04624797::INSTR")
# smu = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2450::04576516::INSTR")
dmm = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEW912502::INSTR")

trim_pass = True
trim_fail = False
reg_dict = {}  # dict for PI05 trim reg addr and value
value_dict = {}  # dict for measure PI05 data after trimed


def smu_sourceV_senseI(pIrange):
    smu.smu_reset()
    # smu.write_cmd(":ROUT:TERM REAR")
    smu.smu_setsourfunc("VOLT")
    smu.smu_setsourceval("VOLT", 0)
    smu.smu_setsourcelimit("VOLT", "ILIMIT", 0.3)
    smu.smu_setsourcerange("VOLT", "AUTO ON")
    smu.smu_setsensefunc("\"CURR\"")
    smu.smu_setsenserange("CURR", pIrange)
    smu.smu_setsensenplc("CURR", 1)


def smu_sourceI_senseV():
    smu.smu_reset()
    # smu.write_cmd(":ROUT:TERM REAR")
    smu.smu_setsourfunc("CURR")
    smu.smu_setsourceval("CURR", 0)
    smu.smu_setsourcelimit("CURR", "VLIMIT", 6)
    smu.smu_setsourcerange("CURR", "AUTO ON")
    smu.smu_setsensefunc("\"VOLT\"")
    smu.smu_setsenserange("VOLT", "AUTO ON")
    smu.smu_setsensenplc("VOLT", 1)


def smu_enable(pFlag):
    if pFlag is True:
        smu.smu_setOutState("ON")
    else:
        smu.smu_setOutState("OFF")


def dmm_osc_init():
    dmm.dmm_setmode("FREQ", "")
    dmm.dmm_setsamp(1)
    dmm.dmm_settrig("IMM")


def dmm_volt_init():
    dmm.dmm_setmode("VOLT", "DC")
    dmm.dmm_setsamp(1)
    dmm.dmm_settrig("IMM")


def ibias_trim():
    """
    trim ibias
    :return: trim result
    """
    smu_sourceV_senseI("AUTO ON")
    set_relay_multi(pBdg, [1, 8], "ON")  # set intb connect to SMU
    pi20_i2c_write(pBdg, pAddr, 0x41, 0x02, 0x0021)  # set intb connect to ibias
    smu_enable(True)
    time.sleep(0.05)
    smu.smu_setsourceval("VOLT", 1)
    time.sleep(0.05)
    ibias = -smu.smu_ins_read()
    # print(ibias)
    if 0.0000009 < ibias < 0.00000119:

        reg_dict["IBIAS_B20A00_[5:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x00)
        value_dict["IBIAS"] = ibias
        smu_enable(False)
        set_relay_unit(pBdg, 0)
        pi20_i2c_write(pBdg, pAddr, 0x41, 0x02, 0x0000)
        return trim_pass
    else:
        for i in range(0x0000, 0x001F + 0x0001, 0x0001):
            pi20_i2c_write(pBdg, pAddr, 0x20, 0x00, i)
            time.sleep(0.05)
            ibias = -smu.smu_ins_read()
            # print(ibias)
            if 0.0000009 < ibias < 0.00000119:
                reg_dict["IBIAS_B20A00_[5:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x00)
                value_dict["IBIAS"] = ibias
                smu_enable(False)
                set_relay_unit(pBdg, 0)
                pi20_i2c_write(pBdg, pAddr, 0x41, 0x02, 0x0000)
                return trim_pass

    reg_dict["IBIAS_B20A00_[5:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x00)
    value_dict["IBIAS"] = ibias
    smu_enable(False)
    set_relay_unit(pBdg, 0)
    pi20_i2c_write(pBdg, pAddr, 0x41, 0x02, 0x0000)
    return trim_fail


def osc_trim():
    """
    trim osc
    :return: trim result
    """
    dmm_osc_init()
    set_relay_multi(pBdg, [1, 2, 5], "ON")  # set intb connect to DMM and pull up intb
    pi20_i2c_write(pBdg, pAddr, 0x41, 0x01, 0x0001)  # set intb connect to osc
    time.sleep(0.05)
    freq = dmm.dmm_ins_read()
    print(freq)
    osc_reg = int(pi20_i2c_read(pBdg, pAddr, 0x22, 0x03), 16)
    if 500000 - 10000 < freq < 500000 + 10000:
        reg_dict["OSC_B22A03_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x03)
        value_dict["OSC"] = freq
        set_relay_unit(pBdg, 0)
        pi20_i2c_write(pBdg, pAddr, 0x41, 0x01, 0x0000)
        return trim_pass
    else:
        for i in range(0x0000, 0x00FF + 0x0001, 0x0001):
            time.sleep(0.05)
            freq = dmm.dmm_ins_read()
            pi20_i2c_write(pBdg, pAddr, 0x22, 0x03, (i << 8) | (osc_reg & 0x00FF))
            if 500000 - 5000 < freq < 500000 + 5000:
                reg_dict["OSC_B22A03_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x03)
                value_dict["OSC"] = freq
                set_relay_unit(pBdg, 0)
                pi20_i2c_write(pBdg, pAddr, 0x41, 0x01, 0x0000)
                return trim_pass

    reg_dict["OSC_B22A03_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x03)
    value_dict["OSC"] = freq
    set_relay_unit(pBdg, 0)
    pi20_i2c_write(pBdg, pAddr, 0x41, 0x01, 0x0000)
    return trim_fail


def vref_utility(pRegSetting):
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x01), 16) & 0xFF00
    pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | pRegSetting)
    time.sleep(0.05)
    verf_val = dmm.dmm_ins_read()
    return verf_val


def vref_trim():
    """
    trim vref
    :return: trim result
    """

    trim_result = trim_pass

    dmm_volt_init()
    set_relay_multi(pBdg, [1, 6], "ON")  # connect verf to DMM
    pi20_i2c_write(pBdg, pAddr, 0x20, 0x00, (0x00C8 << 8) & 0xFF00)
    print(pi20_i2c_read(pBdg, pAddr, 0x20, 0x00))
    pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, (0x0007 << 8) & 0xFF00)
    print(pi20_i2c_read(pBdg, pAddr, 0x20, 0x01))

    vref_val = dmm.dmm_ins_read()
    # vref = []
    # code = []
    if abs(vref_val - 2.5) < 0.002:
        return trim_pass
    else:
        reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x01), 16)
        time.sleep(0.05)
        real_vrefA = dmm.dmm_ins_read()

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | 0x007F)
        time.sleep(0.05)
        real_vrefB = dmm.dmm_ins_read()

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | 0x0080)
        time.sleep(0.05)
        real_vrefC = dmm.dmm_ins_read()

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | 0x00FF)
        time.sleep(0.05)
        real_vrefD = dmm.dmm_ins_read()

        print("vref:", real_vrefA, real_vrefB, real_vrefC, real_vrefD)

        if real_vrefA <= 2.5 <= real_vrefB:
            closest = dichotomy_search([0x00, 0x7F], "incremental", 2.5, vref_utility)
            pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | closest)
            time.sleep(0.05)
            if abs(dmm.dmm_ins_read() - 2.5) < 0.002:
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                trim_result = trim_result and trim_pass
            else:
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                trim_result = trim_result and trim_fail
        elif real_vrefC <= 2.5 <= real_vrefD:
            closest = dichotomy_search([0x80, 0xFF], "incremental", 2.5, vref_utility)
            pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | closest)
            time.sleep(0.05)
            if abs(dmm.dmm_ins_read() - 2.5) < 0.002:
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                trim_result = trim_result and trim_pass
            else:
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                trim_result = trim_result and trim_fail
        else:
            if 2.5 > real_vrefB:
                pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | 0x007F)
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                time.sleep(0.05)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                if abs(value_dict["VREF"] - 2.5) < 0.002:
                    trim_result = trim_result and trim_pass
                else:
                    trim_result = trim_result and trim_fail
            elif 2.5 < real_vrefC:
                pi20_i2c_write(pBdg, pAddr, 0x20, 0x01, reg_temp | 0x0080)
                reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
                time.sleep(0.05)
                value_dict["VREF"] = dmm.dmm_ins_read()
                # set_relay_unit(pBdg, 0)
                if abs(value_dict["VREF"] - 2.5) < 0.002:
                    trim_result = trim_result and trim_pass
                else:
                    trim_result = trim_result and trim_fail

    # reg_dict["VREF_B20A01_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x01)
    # value_dict["VREF"] = dmm.dmm_ins_read
    # set_relay_unit(pBdg, 0)
    return trim_result


def idac_trim():
    """
    trim idac
    :return: trim result
    """
    ideal_gain = 0.13125  # 0x0F00 cur - 0x0100 cur
    ideal_offset = 0.009375  # 0x0100 cut

    buck_enable(pBdg, pAddr, True)
    set_buck_output_code(pBdg, pAddr, 0x0B85)  # power supply for IDAC

    trim_result = trim_pass
    set_relay_multi(pBdg, [3, 8], "ON")
    smu_sourceV_senseI("AUTO ON")

    reg_temp_gain = int(pi20_i2c_read(pBdg, pAddr, 0x21, 0x00), 16)
    reg_temp_offset = int(pi20_i2c_read(pBdg, pAddr, 0x22, 0x00), 16)
    smu_enable(True)
    print("idac gain")
    '''*******************************************idac gain trim*****************************************'''
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0002)  # enable IDAC
    idac_cur_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
    idac_cur_F00 = -smu.smu_ins_read()
    real_gainA = (idac_cur_F00 - idac_cur_100)

    pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | 0x007F)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    idac_cur_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
    idac_cur_F00 = -smu.smu_ins_read()
    real_gainB = (idac_cur_F00 - idac_cur_100)

    pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | 0x0080)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    idac_cur_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
    idac_cur_F00 = -smu.smu_ins_read()
    real_gainC = (idac_cur_F00 - idac_cur_100)

    pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | 0x00FF)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    idac_cur_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
    idac_cur_F00 = -smu.smu_ins_read()
    real_gainD = (idac_cur_F00 - idac_cur_100)

    print("IDAC Gain", real_gainA, real_gainB, real_gainC, real_gainD, ideal_gain)

    if real_gainA <= ideal_gain <= real_gainB:
        low = 0x0000
        high = 0x007F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | mid)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
            idac_cur_100 = -smu.smu_ins_read()
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
            idac_cur_F00 = -smu.smu_ins_read()
            diff = abs((idac_cur_F00 - idac_cur_100) - ideal_gain)
            # print((idac_cur_F00 - idac_cur_100))
            if diff < mid_diff:
                mid_diff = diff
                closest = reg_temp_gain | mid
            if abs(idac_cur_F00 - idac_cur_100) < ideal_gain:
                low = mid + 1
            elif abs(idac_cur_F00 - idac_cur_100) > ideal_gain:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
                break

        pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, closest)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
        idac_cur_100 = -smu.smu_ins_read()
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
        idac_cur_F00 = -smu.smu_ins_read()
        print(abs(idac_cur_F00 - idac_cur_100))

        if abs(idac_cur_F00 - idac_cur_100) - ideal_gain < 0.0004:
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = abs(idac_cur_F00 - idac_cur_100)
            trim_result = trim_result and trim_pass
        else:
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = abs(idac_cur_F00 - idac_cur_100)
            trim_result = trim_result and trim_fail
    elif real_gainC <= ideal_gain <= real_gainD:
        low = 0x0080
        high = 0x00FF
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | mid)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
            idac_cur_100 = -smu.smu_ins_read()
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
            idac_cur_F00 = -smu.smu_ins_read()
            diff = abs((idac_cur_F00 - idac_cur_100) - ideal_gain)

            if diff < mid_diff:
                mid_diff = diff
                closest = reg_temp_gain | mid
            if abs(idac_cur_F00 - idac_cur_100) < ideal_gain:
                low = mid + 1
            elif abs(idac_cur_F00 - idac_cur_100) > ideal_gain:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
                break

        pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, closest)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
        idac_cur_100 = -smu.smu_ins_read()
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
        idac_cur_F00 = -smu.smu_ins_read()
        print(abs(idac_cur_F00 - idac_cur_100))

        if abs(idac_cur_F00 - idac_cur_100) - ideal_gain < 0.0004:
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            print(closest)
            print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = abs(idac_cur_F00 - idac_cur_100)
            # set_relay_unit(pBdg, 0)
            trim_result = trim_result and trim_pass
        else:
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            print(closest)
            print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = abs(idac_cur_F00 - idac_cur_100)
            # set_relay_unit(pBdg, 0)
            trim_result = trim_result and trim_fail
    else:
        final_gain = 0
        if ideal_gain >= real_gainB:
            pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | 0x007F)
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            # print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = real_gainB
            # trim_result = trim_result and trim_fail
            final_gain = real_gainB
        elif ideal_gain <= real_gainC:
            pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp_gain | 0x0080)
            reg_dict["IDAC_gain_B21A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x00)
            # print(reg_dict["IDAC_gain_B21A00_[7:0]"])
            value_dict["idac_gain"] = real_gainC
            # trim_result = trim_result and trim_fail
            final_gain = real_gainB
        if abs(final_gain - ideal_gain) < 0.0004:
            trim_result = trim_result and trim_pass
        else:
            trim_result = trim_result and trim_fail
    print("IDAC gain result:", trim_result)
    '''*******************************************idac offset trim*****************************************'''
    print("idac offset")
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    idac_cur_100 = -smu.smu_ins_read()
    real_offsetA = idac_cur_100

    pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (0x007F << 8) | reg_temp_offset)
    idac_cur_100 = -smu.smu_ins_read()
    real_offsetB = idac_cur_100

    pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (0x0080 << 8) | reg_temp_offset)
    idac_cur_100 = -smu.smu_ins_read()
    real_offsetC = idac_cur_100

    pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (0x00FF << 8) | reg_temp_offset)
    idac_cur_100 = -smu.smu_ins_read()
    real_offsetD = idac_cur_100

    print("IDAC Offset:", real_offsetA, real_offsetB, real_offsetC, real_offsetD, ideal_offset)

    if real_offsetB <= ideal_offset <= real_offsetA:
        low = 0x0000
        high = 0x007F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (mid << 8) | reg_temp_offset)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
            idac_cur_100 = -smu.smu_ins_read()
            diff = abs(idac_cur_100 - ideal_offset)

            if diff < mid_diff:
                mid_diff = diff
                closest = (mid << 8) | reg_temp_offset
            if idac_cur_100 > ideal_offset:
                low = mid + 1
            elif idac_cur_100 < ideal_offset:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
                break

        pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, closest)
        idac_cur_100 = -smu.smu_ins_read()
        print(abs(idac_cur_100 - ideal_offset))
        if abs(idac_cur_100 - ideal_offset) < 0.0003:
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = idac_cur_100
            trim_result = trim_result and trim_pass
        else:
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = idac_cur_100
            trim_result = trim_result and trim_fail
    elif real_offsetC <= ideal_offset <= real_offsetD:
        low = 0x0080
        high = 0x00FF
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (mid << 8) | reg_temp_offset)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
            idac_cur_100 = -smu.smu_ins_read()
            diff = abs(idac_cur_100 - ideal_offset)

            if diff < mid_diff:
                mid_diff = diff
                closest = (mid << 8) | reg_temp_offset
            if idac_cur_100 < ideal_offset:
                low = mid + 1
            elif idac_cur_100 > ideal_offset:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
                break

        pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, closest)
        idac_cur_100 = -smu.smu_ins_read()
        print(abs(idac_cur_100 - ideal_offset))
        if abs(idac_cur_100 - ideal_offset) < 0.0003:
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = idac_cur_100
            trim_result = trim_result and trim_pass
        else:
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = idac_cur_100
            trim_result = trim_result and trim_fail
    else:
        final_offset = 0
        if ideal_offset > real_offsetD:
            pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (0x00FF << 8) | reg_temp_offset)
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = real_offsetD
            final_offset = real_offsetD
            # trim_result = trim_result and trim_fail
        elif ideal_offset < real_offsetB:
            pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (0x007F << 8) | reg_temp_offset)
            reg_dict["IDAC_offset_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
            print(reg_dict["IDAC_offset_B22A00_[15:8]"])
            value_dict["idac_offset"] = real_offsetB
            final_offset = real_offsetB
            # trim_result = trim_result and trim_fail
        if abs(final_offset - ideal_offset) < 0.003:
            trim_result = trim_result and trim_pass
        else:
            trim_result = trim_result and trim_fail

    print("IDAC offset result:", trim_result)
    smu_enable(False)
    # set_relay_unit(pBdg, 0)
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0000)  # disable IDAC
    return trim_result


def vdac_trim():
    """
    trim vdac
    :return: trim result
    """
    trim_result = trim_pass

    ideal_gain = 2.187  # 0x0F00 vol - 0x0100 vol
    ideal_offset = 0.156  # 0x0100 vol

    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x000E)

    set_relay_multi(pBdg, [3, 7], "ON")
    smu_sourceI_senseV()
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x05, 0x0001)  # set VDAC gain and range -2.5V
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0001)  # enable VDAC

    smu_enable(True)
    '''*******************************************vdac gain trim*****************************************'''

    reg_temp_offset = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x02), 16)
    vdac_vol_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
    vdac_vol_F00 = -smu.smu_ins_read()
    real_gainA = abs(vdac_vol_F00 - vdac_vol_100)

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (0x001F << 8) | reg_temp_offset)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
    vdac_vol_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
    vdac_vol_F00 = -smu.smu_ins_read()
    real_gainB = abs(vdac_vol_F00 - vdac_vol_100)

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (0x0020 << 8) | reg_temp_offset)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
    vdac_vol_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
    vdac_vol_F00 = -smu.smu_ins_read()
    real_gainC = abs(vdac_vol_F00 - vdac_vol_100)

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (0x003F << 8) | reg_temp_offset)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
    vdac_vol_100 = -smu.smu_ins_read()
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
    vdac_vol_F00 = -smu.smu_ins_read()
    real_gainD = abs(vdac_vol_F00 - vdac_vol_100)

    print("VDAC Gain:", real_gainA, real_gainB, real_gainC, real_gainD, ideal_gain)

    if real_gainA <= ideal_gain <= real_gainB:
        low = 0x0000
        high = 0x001F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (mid << 8) | reg_temp_offset)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
            vdac_vol_100 = -smu.smu_ins_read()
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
            vdac_vol_F00 = -smu.smu_ins_read()
            diff = abs(abs(vdac_vol_F00 - vdac_vol_100) - ideal_gain)

            if diff < mid_diff:
                mid_diff = diff
                closest = (mid << 8) | reg_temp_offset
            if abs(vdac_vol_F00 - vdac_vol_100) < ideal_gain:
                low = mid + 1
            elif abs(vdac_vol_F00 - vdac_vol_100) > ideal_gain:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
                break

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, closest)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
        vdac_vol_100 = -smu.smu_ins_read()
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
        vdac_vol_F00 = -smu.smu_ins_read()
        print(abs(vdac_vol_F00 - vdac_vol_100))

        if abs(abs(vdac_vol_F00 - vdac_vol_100) - ideal_gain) < 0.002:
            reg_dict["VDAC_gain_B20A02_[13:8]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            print(reg_dict["VDAC_gain_B20A02_[13:8]"])
            value_dict["vdac_gain"] = abs(vdac_vol_F00 - vdac_vol_100)
            trim_result = trim_result and trim_pass
        else:
            reg_dict["VDAC_gain_B20A02_[13:8]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            print(reg_dict["VDAC_gain_B20A02_[13:8]"])
            value_dict["vdac_gain"] = abs(vdac_vol_F00 - vdac_vol_100)
            trim_result = trim_result and trim_fail
    elif real_gainC <= ideal_gain <= real_gainD:
        low = 0x0020
        high = 0x003F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (mid << 8) | reg_temp_offset)
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
            vdac_vol_100 = -smu.smu_ins_read()
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
            vdac_vol_F00 = -smu.smu_ins_read()
            diff = abs(abs(vdac_vol_F00 - vdac_vol_100) - ideal_gain)

            if diff < mid_diff:
                mid_diff = diff
                closest = (mid << 8) | reg_temp_offset
            if abs(vdac_vol_F00 - vdac_vol_100) < ideal_gain:
                low = mid + 1
            elif abs(vdac_vol_F00 - vdac_vol_100) > ideal_gain:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
                break

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, closest)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set VDAC code
        vdac_vol_100 = -smu.smu_ins_read()
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
        vdac_vol_F00 = -smu.smu_ins_read()
        print(abs(vdac_vol_F00 - vdac_vol_100))

        if abs(abs(vdac_vol_F00 - vdac_vol_100) - ideal_gain) < 0.002:
            reg_dict["VDAC_gain_B20A02_[13:8]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            print(reg_dict["VDAC_gain_B20A02_[13:8]"])
            value_dict["vdac_gain"] = abs(vdac_vol_F00 - vdac_vol_100)
            trim_result = trim_result and trim_pass
        else:
            reg_dict["VDAC_gain_B20A02_[13:8]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            print(reg_dict["VDAC_gain_B20A02_[13:8]"])
            value_dict["vdac_gain"] = abs(vdac_vol_F00 - vdac_vol_100)
            trim_result = trim_result and trim_fail
    print("VDAC gain result:", trim_result)
    '''*******************************************vdac offset trim*****************************************'''
    reg_temp_gain = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x02), 16)
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0F00)  # set VDAC code
    real_offsetA = -smu.smu_ins_read()

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp_gain | 0x000F)
    real_offsetB = -smu.smu_ins_read()

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp_gain | 0x0010)
    real_offsetC = -smu.smu_ins_read()

    pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp_gain | 0x001F)
    real_offsetD = -smu.smu_ins_read()

    print("VDAC Offset:", real_offsetA, real_offsetB, real_offsetC, real_offsetD, ideal_offset)

    if real_offsetA >= ideal_offset >= real_offsetB:
        low = 0x0000
        high = 0x000F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp_gain | mid)
            vdac_vol_F00 = -smu.smu_ins_read()
            diff = abs(vdac_vol_F00 - ideal_offset)

            if diff < mid_diff:
                mid_diff = diff
                closest = reg_temp_gain | mid
            if vdac_vol_F00 > ideal_offset:
                low = mid + 1
            elif vdac_vol_F00 < ideal_offset:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
                break

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, closest)
        vdac_vol_F00 = -smu.smu_ins_read()

        if abs(vdac_vol_F00 - ideal_offset) < 0.005:
            reg_dict["VDAC_offset_B20A02_[4:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            # print(reg_dict["VDAC_offset_B20A02_[4:0]"])
            value_dict["vdac_offset"] = vdac_vol_F00
            trim_result = trim_result and trim_pass
        else:
            reg_dict["VDAC_offset_B20A02_[4:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            # print(reg_dict["VDAC_offset_B20A02_[4:0]"])
            value_dict["vdac_offset"] = vdac_vol_F00
            trim_result = trim_result and trim_fail
    elif real_offsetD <= ideal_offset <= real_offsetC:
        low = 0x0010
        high = 0x001F
        closest = None
        mid_diff = float('inf')
        while low <= high:
            mid = (low + high) // 2

            pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp_gain | mid)
            vdac_vol_F00 = -smu.smu_ins_read()
            diff = abs(vdac_vol_F00 - ideal_offset)

            if diff < mid_diff:
                mid_diff = diff
                closest = reg_temp_gain | mid
            if vdac_vol_F00 < ideal_offset:
                low = mid + 1
            elif vdac_vol_F00 > ideal_offset:
                high = mid - 1
            else:
                closest = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
                break

        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, closest)
        vdac_vol_F00 = -smu.smu_ins_read()

        if abs(vdac_vol_F00 - ideal_offset) < 0.005:
            reg_dict["VDAC_offset_B20A02_[4:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            # print(reg_dict["VDAC_offset_B20A02_[4:0]"])
            value_dict["vdac_offset"] = vdac_vol_F00
            trim_result = trim_result and trim_pass
        else:
            reg_dict["VDAC_offset_B20A02_[4:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x02)
            # print(reg_dict["VDAC_offset_B20A02_[4:0]"])
            value_dict["vdac_offset"] = vdac_vol_F00
            trim_result = trim_result and trim_fail
    print("VDAC offset result:", trim_result)
    smu_enable(False)
    set_relay_unit(pBdg, 0)
    return trim_result


def vdac_isns_utility(pRegSetting):
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x03), 16) & 0xFF80
    pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | pRegSetting)
    smu.smu_setsourceval("CURR", 0)
    vdac_isns_0 = adc_avr(pBdg, pAddr, 4)
    smu.smu_setsourceval("CURR", 0.05)
    vdac_isns_1 = adc_avr(pBdg, pAddr, 4)
    real_val = abs(vdac_isns_1 - vdac_isns_0)
    print(real_val)
    return real_val


def vdac_isns_trim():
    """
    trim vdac isns
    :return: trim result
    """
    trim_result = trim_pass

    ideal_val = 1640

    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x0010)

    set_relay_multi(pBdg, [3, 7], "ON")
    smu_sourceI_senseV()
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x05, 0x0001)  # set VDAC gain and range -2.5V
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0800)  # set VDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0001)  # enable VDAC

    smu_enable(True)
    adc_config(pBdg, pAddr, 4, 1, 0)
    '''**************************************** vdac isns trim ****************************************************'''
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x03), 16) & 0xFF80
    minmax_point = [0x0000, 0x003F, 0x0040, 0x007F]
    real_val = []
    for point in minmax_point:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | point)
        smu.smu_setsourceval("CURR", 0)
        vdac_isns_0 = adc_avr(pBdg, pAddr, 4)
        smu.smu_setsourceval("CURR", 0.05)
        vdac_isns_1 = adc_avr(pBdg, pAddr, 4)
        real_val.append(abs(vdac_isns_1 - vdac_isns_0))

    check_val = 0

    if real_val[0] <= ideal_val <= real_val[1]:
        closest = dichotomy_search([0x0000, 0x003F], "incremental", ideal_val, vdac_isns_utility)
        # vdac_isns_utility(closest)
        check_val = vdac_isns_utility(closest)
    elif real_val[2] <= ideal_val <= real_val[3]:
        closest = dichotomy_search([0x0040, 0x007F], "incremental", ideal_val, vdac_isns_utility)
        # vdac_isns_utility(closest)
        check_val = vdac_isns_utility(closest)
    elif ideal_val < real_val[0]:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | 0x0000)
        check_val = vdac_isns_utility(0x0000)
    elif ideal_val > real_val[1]:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | 0x003F)
        check_val = vdac_isns_utility(0x0040)
    elif ideal_val < real_val[2]:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | 0x0040)
        check_val = vdac_isns_utility(0x0041)
    elif ideal_val > real_val[3]:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | 0x007F)
        check_val = vdac_isns_utility(0x007F)

    if check_val - ideal_val < 2:
        reg_dict["VDAC_ISNS_B20A03_[6:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x03)
        print(reg_dict["VDAC_ISNS_B20A03_[6:0]"])
        value_dict["VDAC_ISNS_ADC_READ"] = check_val
        smu_enable(False)
        set_relay_unit(pBdg, 0)
        return trim_pass
    else:
        reg_dict["VDAC_ISNS_B20A03_[6:0]"] = pi20_i2c_read(pBdg, pAddr, 0x20, 0x03)
        # print(reg_dict["TIAN_B21A01_[8:0]"])
        value_dict["VDAC_ISNS_ADC_READ"] = check_val
        smu_enable(False)
        set_relay_unit(pBdg, 0)
        return trim_fail


def tian_utility(pRegSetting):
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x21, 0x01), 16) & 0xFE00
    pi20_i2c_write(pBdg, pAddr, 0x21, 0x01, reg_temp | pRegSetting)
    smu.smu_setsourceval("CURR", 0.001024)
    TIA_VAL1 = adc_avr(pBdg, pAddr, 0)
    smu.smu_setsourceval("CURR", 0.003072)
    TIA_VAL2 = adc_avr(pBdg, pAddr, 0)
    real_val = abs(TIA_VAL1 - TIA_VAL2)
    print(real_val)
    return real_val


def tian_tian():
    """
    trim TIAN
    :return: trim result
    """

    ideal_val = 1638

    set_relay_multi(pBdg, [4, 8], "ON")
    smu_sourceI_senseV()
    smu_enable(True)
    pi20_i2c_write(pBdg, pAddr, 0x11, 0x00, 0x0207)
    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x000E)

    adc_config(pBdg, pAddr, 12, 1, 1)

    pi20_i2c_write(pBdg, pAddr, 0x01, 0x0F, 0x0000)

    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x21, 0x01), 16)

    smu.smu_setsourceval("CURR", 0.001024)
    TIA_VAL1 = adc_avr(pBdg, pAddr, 0)
    smu.smu_setsourceval("CURR", 0.003072)
    TIA_VAL2 = adc_avr(pBdg, pAddr, 0)
    real_valA = abs(TIA_VAL1 - TIA_VAL2)

    pi20_i2c_write(pBdg, pAddr, 0x21, 0x01, (reg_temp << 9) | 0x01FF)
    smu.smu_setsourceval("CURR", 0.001024)
    TIA_VAL1 = adc_avr(pBdg, pAddr, 0)
    smu.smu_setsourceval("CURR", 0.003072)
    TIA_VAL2 = adc_avr(pBdg, pAddr, 0)
    real_valB = abs(TIA_VAL1 - TIA_VAL2)

    print("TIAN RGain", real_valA, real_valB)

    # xdata = []
    # ydata = []
    # for k in range(0x0000, 0x01FF + 0x0010, 0x0010):
    #     xdata.append(k)
    #     pi20_i2c_write(pBdg, pAddr, 0x21, 0x01, (reg_temp << 9) | k)
    #     smu.smu_setsourceval("CURR", 0.001024)
    #     TIA_VAL1 = adc_avr(pBdg, pAddr, 0)
    #     smu.smu_setsourceval("CURR", 0.003072)
    #     TIA_VAL2 = adc_avr(pBdg, pAddr, 0)
    #     real_val = abs(TIA_VAL1 - TIA_VAL2)
    #     ydata.append(real_val)
    #
    # print_function(xdata, ydata, "TAIN")

    if real_valA <= ideal_val <= real_valB:
        closest = dichotomy_search([0x0000, 0x01FF], "incremental", ideal_val, tian_utility)
        tian_utility(closest)
        check_val = tian_utility(closest)
        if check_val - 1638 < 2:
            reg_dict["TIAN_B21A01_[8:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x01)
            print(reg_dict["TIAN_B21A01_[8:0]"])
            value_dict["TIAN_ADC_READ"] = check_val
            smu_enable(False)
            set_relay_unit(pBdg, 0)
            return trim_pass
        else:
            reg_dict["TIAN_B21A01_[8:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x01)
            # print(reg_dict["TIAN_B21A01_[8:0]"])
            value_dict["TIAN_ADC_READ"] = check_val
            smu_enable(False)
            set_relay_unit(pBdg, 0)
            return trim_fail
    elif ideal_val < real_valA:
        pi20_i2c_write(pBdg, pAddr, 0x21, 0x01, (reg_temp << 9) | 0x0000)
        reg_dict["TIAN_B21A01_[8:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x01)
        # print(reg_dict["TIAN_B21A01_[8:0]"])
        value_dict["TIAN_ADC_READ"] = real_valA
        smu_enable(False)
        set_relay_unit(pBdg, 0)
        return trim_fail
    elif ideal_val > real_valB:
        pi20_i2c_write(pBdg, pAddr, 0x21, 0x01, (reg_temp << 9) | 0x01FF)
        reg_dict["TIAN_B21A01_[8:0]"] = pi20_i2c_read(pBdg, pAddr, 0x21, 0x01)
        # print(reg_dict["TIAN_B21A01_[8:0]"])
        value_dict["TIAN_ADC_READ"] = real_valB
        smu_enable(False)
        set_relay_unit(pBdg, 0)
        return trim_fail


def sweep_idac_offset_gain():
    buck_enable(pBdg, pAddr, True)
    set_buck_output_code(pBdg, pAddr, 0x0B85)
    x = range(0x0000, 0x00FF + 0x0001, 0x0001)
    y = []
    set_relay_multi(pBdg, [3, 8], "ON")
    smu_sourceV_senseI("10E-1")
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0002)  # enable IDAC
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x22, 0x00), 16)
    smu_enable(True)
    for i in x:
        pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (i << 8) | reg_temp)
        idac_cur = -smu.smu_ins_read()
        y.append(idac_cur)

    print_function(x, y, "IDAC offset trim reg")

    x1 = range(0x0000, 0x00FF + 0x0001, 0x0001)
    y1 = []
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x21, 0x00), 16)
    for i in x:
        pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, reg_temp | i)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0100)  # set IDAC code
        idac_cur1 = -smu.smu_ins_read()
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0F00)  # set IDAC code
        idac_cur2 = -smu.smu_ins_read()
        y1.append(abs(idac_cur2 - idac_cur1))

    print_function(x1, y1, "IDAC gain trimreg")
    smu_enable(False)
    buck_enable(pBdg, pAddr, False)


def sweep_vdac_offset_gain():
    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x000E)
    x = range(0x0000, 0x001F + 0x0001, 0x0001)
    y = []
    set_relay_multi(pBdg, [3, 7], "ON")
    smu_sourceI_senseV()
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x05, 0x0001)  # set vdac gain and range
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0100)  # set IDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0001)  # enable vdac
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x02), 16)
    smu_enable(True)
    for i in x:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, reg_temp | i)
        vdac_vol = smu.smu_ins_read()
        y.append(vdac_vol)

    print_function(x, y, "vdac offset trim reg")

    x1 = range(0x0000, 0x003F + 0x0001, 0x0001)
    y1 = []
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x02), 16)
    for i in x1:
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x02, (i << 8) | reg_temp)
        vdac_vol = smu.smu_ins_read()
        y1.append(vdac_vol)

    print_function(x1, y1, "vdac gain trim reg")
    smu_enable(False)
    nrail_enable(pBdg, pAddr, False)


def sweep_tian():
    set_relay_multi(pBdg, [4, 8], "ON")
    smu_sourceI_senseV()
    smu_enable(True)
    pi20_i2c_write(pBdg, pAddr, 0x11, 0x00, 0x0207)

    adc_config(pBdg, pAddr, 12, 1, 1)

    pi20_i2c_write(pBdg, pAddr, 0x01, 0x0F, 0x0000)
    tian_utility(0x0100)
    smu.smu_setsourceval("CURR", 0.001024)
    xdata = []
    ydata = []
    for i in range(100):
        ydata.append(adc_avr(pBdg, pAddr, 0))
        xdata.append(i)
    print(ydata)
    print_function(xdata, ydata, "TIAN ADC TEST")
    smu_enable(False)
    set_relay_unit(pBdg, 0)


def sweep_vdac_isns():
    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x000F)
    x = range(0x0000, 0x007F + 0x0001, 0x0001)
    y = []
    set_relay_multi(pBdg, [3, 7], "ON")
    smu_sourceI_senseV()
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x05, 0x0001)  # set vdac gain and range
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x00, 0x0800)  # set IDAC code
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0001)  # enable vdac
    reg_temp = int(pi20_i2c_read(pBdg, pAddr, 0x20, 0x03), 16)
    smu_enable(True)
    time.sleep(0.1)
    smu.smu_ins_read()
    time.sleep(0.1)
    adc_config(pBdg, pAddr, 4, 1, 0)
    for i in x:
        smu.smu_setsourceval("CURR", 0)
        time.sleep(0.05)
        pi20_i2c_write(pBdg, pAddr, 0x20, 0x03, reg_temp | i)
        vdac_isns_0 = adc_avr(pBdg, pAddr, 4)
        smu.smu_setsourceval("CURR", 0.05)
        time.sleep(0.05)
        vdac_isns_1 = adc_avr(pBdg, pAddr, 4)
        y.append(abs(vdac_isns_1 - vdac_isns_0))
        print(abs(vdac_isns_1 - vdac_isns_0))

    print_function(x, y, "vdac ISNS trim reg")


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    start_time = time.time()
    np.set_printoptions(suppress=True)  # 取消科学计数法输出

    set_relay_unit(pBdg, 0)
    device_reset(pBdg, pAddr)
    time.sleep(0.05)
    pi_err_check(device_unlock(pBdg, pAddr))
    pi_err_check(check_device_id(pBdg, pAddr))
    time.sleep(0.05)
    final_result = True
    # sweep_vdac_isns()
    # sweep_idac_offset_gain()
    # quit()
    # sweep_vdac_offset_gain()

    if ibias_trim():
        print("IBIAS trimming pass")
    else:
        print("IBIAS trimming fail")
        final_result = final_result and False

    if osc_trim():
        print("OSC trimming pass")
    else:
        print("OSC trimming fail")
        final_result = final_result and False

    if vref_trim():
        print("vref trimming pass")
    else:
        print("vref trimming fail")
        final_result = final_result and False

    # quit()
    if idac_trim():
        print("IDAC trimming pass")
    else:
        print("IDAC trimming fail")
        final_result = final_result and False

    if vdac_trim():
        print("VDAC trimming pass")
    else:
        print("VDAC trimming fail")
        final_result = final_result and False

    if vdac_isns_trim():
        print("vdac_isns trimming pass")
    else:
        print("vdac_isns trimming fail")
        final_result = final_result and False

    if tian_tian():
        print("TIAN trimming pass")
    else:
        print("TIAN trimming fail")
        final_result = final_result and False

    print(reg_dict)
    print(value_dict)

    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(r"D:\testrecord\PI20\trim\pi20_trim.xlsx")
    sheet = wb.sheets[0]

    write_data_to_excel(sheet, "b2", "b2", "b2", "b%d" % len(list(reg_dict.keys())), 0, list(reg_dict.keys()))
    write_data_to_excel(sheet, "c2", "c2", "c2", "c%d" % len(list(reg_dict.values())), 0, list(reg_dict.values()))

    write_data_to_excel(sheet,
                        "b%d" % (2 + len(list(reg_dict.keys()))),
                        "b%d" % (2 + len(list(reg_dict.keys()))),
                        "b%d" % (2 + len(list(reg_dict.keys()))),
                        "b%d" % (2 + len(list(reg_dict.keys())) + len(list(value_dict.keys()))),
                        0, list(value_dict.keys()))
    write_data_to_excel(sheet,
                        "c%d" % (2 + len(list(reg_dict.values()))),
                        "c%d" % (2 + len(list(reg_dict.values()))),
                        "c%d" % (2 + len(list(reg_dict.values()))),
                        "c%d" % (2 + len(list(reg_dict.values())) + len(list(value_dict.values()))),
                        0, list(value_dict.values()))
    sheet.api.Cells.HorizontalAlignment = -4108
    sheet.api.Cells.VerticalAlignment = -4108
    sheet.autofit("columns")
    wb.save()
    wb.close()
    app.quit()

    pi20_i2c_write(pBdg, pAddr, 0x21, 0x02, 0x0F8C)  # 2MHz 0F8C 4MHz 0780
    end_time = time.time()
    total_time = end_time - start_time
    print("Total runtime:", total_time, "seconds")
    print("PI20 Trim Final Result:", final_result)
    print("end")
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
