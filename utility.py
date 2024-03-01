# -*- encoding: utf-8 -*-
"""
    @File : utility.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/27 10:12 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/27 10:12 \n
"""
import numpy as np

from subM_brig_ch32.pi20_drvier import *
import pyvisa
import xlwings as xw
import matplotlib.pyplot as plt

PI_OK = 0
PI_ERR = -1

pBdg = hid.device()  # create hid device
pBdg.open(0x1A86, 0xFE07)
pAddr = 0x80
rm = pyvisa.ResourceManager()


# for ins_id in rm.list_resources():
#     if "::0::" in ins_id:
#         pass
#     else:
#         print(ins_id)


def device_reset(pHid, pDeviceAdd):
    """
    soft reset device
    :param pHid: hid object
    :param pDeviceAdd:device slave address
    :return: None
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x01, 0x01, 0x0001)


def device_unlock(pHid, pDeviceAdd):
    """
    unlock device
    :param pHid: hid object
    :param pDeviceAdd:device slave address
    :return: PI_OK or PI_ERR
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x40, 0x00, 0xC0DE)
    pi20_i2c_write(pHid, pDeviceAdd, 0x40, 0x01, 0xF00D)

    if (pi20_i2c_read(pHid, pDeviceAdd, 0x40, 0x00) == "%04X" % 0xC0DE
            and pi20_i2c_read(pHid, pDeviceAdd, 0x40, 0x01) == "%04X" % 0xF00D):
        return PI_OK
    else:
        return PI_ERR


def check_device_id(pHid, pDeviceAdd):
    """
    check device id at reg B00A01
    :param pHid: hid object
    :param pDeviceAdd: device slave address
    :return: PI_OK or PI_ERR
    """
    device_id = pi20_i2c_read(pHid, pDeviceAdd, 0x00, 0x01)
    print(device_id)
    if device_id == "%04X" % 0x20A0:
        return PI_OK
    else:
        return PI_ERR


def pi_err_check(pErr):
    if pErr == PI_OK:
        pass
    else:
        print("Error: %d" % pErr)
        quit(pErr)


def write_data_to_excel(pSheet, pXStart, pYStart, pXEnd, pYEnd, pXData, pYData):
    """
    write data to Excel
    :param pSheet:  sheet of Excel
    :param pXStart: start position of row
    :param pYStart: start position of column
    :param pXEnd: end position of row
    :param pYEnd: end position of column
    :param pXData: row data to be written
    :param pYData: column data to be written
    :return: None
    """

    if pXStart == pXEnd:
        pSheet[pYStart].options(transpose=True).value = pYData
    elif pYStart == pYEnd:
        pSheet[pXStart].value = pXData
    else:
        pSheet[pXStart].value = pXData
        pSheet[pYStart].options(transpose=True).value = pYData


def set_relay_unit(pHidBridge, relayNum):
    """
    This function used to turn on the relay and turn off all relay
    :param pHidBridge: hid object
    :param relayNum: the relay you want to turn on when it equl 0 will turn of all relay
    :return: None
    """
    if 0 < relayNum <= 8:
        i2c_write(pHidBridge, 0xE0, 0x00, [0x03, (0x01 << relayNum - 1) ^ 0xFF])  # i2c slave_addr is 0xE0
        # print(bin(0x01 << relyNum))
    elif relayNum == 0:
        i2c_write(pHidBridge, 0xE0, 0x00, [0x03, 0xFF])  # i2c slave_addr is 0xE0


def set_relay_multi(pHidBridge, pPos, pStatus):
    """
    This function used to turn on multichannel relay from start to end and turn off all relay
    :param pHidBridge: hid object
    :param pPos: relay need to be turned on (list length is 8)
    :param pStatus: ON or OFF
    :return: None
    """
    if 1 <= len(pPos) <= 8:
        relay_pos = 0xFF
        if pStatus == "ON":
            for i in pPos:
                relay_pos = (0x01 << (i - 1)) ^ relay_pos
        else:
            relay_pos = 0xFF

        i2c_write(pHidBridge, 0xE0, 0x00, [0x03, relay_pos])  # i2c slave_addr is 0xE0
    else:
        print("parameter error")


def print_function(px, py, pTitle):
    plt.figure(figsize=(1080 / 100, 1080 / 100), dpi=100)
    plt.scatter(px, py)  # 绘制离散函数图像
    plt.xlabel('x')  # 设置x轴标签
    plt.ylabel('f(x)')  # 设置y轴标签
    plt.title(pTitle)  # 设置图像标题
    plt.xticks(np.arange(px[0], px[-1] + px[0], int((px[-1] - px[0]) / len(px) * 10)))
    ymin = min(py)
    ymax = max(py)
    stepsize = (ymax - ymin) / len(py)
    plt.yticks(np.arange(ymin, ymax + stepsize, stepsize * 10), fontsize=8)
    plt.show()  # 显示图像


def nrail_enable(pHid, pDeviceAdd, pEnableFlag):
    """
    Enable or Disable NRAIL
    :param pHid: hid device object
    :param pDeviceAdd: device slave address
    :param pEnableFlag: flag to set buck enable(1) or disable(0)
    :return: None
    """
    if pEnableFlag is True:
        pi20_i2c_write(pHid, pDeviceAdd, 0x06, 0x00, 0x0061)
    else:
        pi20_i2c_write(pHid, pDeviceAdd, 0x06, 0x00, 0x0060)


def set_nrail_output_code(pHid, pDeviceAdd, pOutputCode):
    """
    Set NRAIL Output Code
    :param pHid: hid device object
    :param pDeviceAdd: device slave address
    :param pOutputCode: output code
    :return: None
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x06, 0x01, pOutputCode)


def buck_enable(pHid, pDeviceAdd, pEnableFlag):
    """
    Enable or Disable Buck
    :param pHid: hid device object
    :param pDeviceAdd: device slave address
    :param pEnableFlag: flag to set buck enable(1) or disable(0)
    :return: None
    """
    if pEnableFlag is True:
        pi20_i2c_write(pHid, pDeviceAdd, 0x07, 0x00, 0x0001)
    else:
        pi20_i2c_write(pHid, pDeviceAdd, 0x07, 0x00, 0x0000)


def adc_config(pHid, pDeviceAdd, pCH, pADCRange, pHiz):
    pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x32, 0x000F)
    pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x33, 0x0089)
    if pADCRange == 1:
        pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x00, (0x03C0 + pCH) | (pHiz << 5))
    else:
        pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x00, (0x03D0 + pCH) | (pHiz << 5))


def adc_read(pHid, pDeviceAdd, pCH):
    val = pi20_i2c_read(pHid, pDeviceAdd, 0x04, pCH)
    return val


def adc_avr(pHid, pDeviceAdd, pCH):
    time.sleep(0.1)
    val = 0
    for i in range(8):
        val += int(adc_read(pHid, pDeviceAdd, pCH), 16)
        time.sleep(0.1)
    return int(val/8)


def set_buck_output_code(pHid, pDeviceAdd, pOutputCode):
    """
    Set Buck Output Code
    :param pHid: hid device object
    :param pDeviceAdd: device slave address
    :param pOutputCode: output code
    :return: None
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x07, 0x01, pOutputCode)


def dichotomy_search(pInterval, pMonotonicity, pAimVal, pFunc):
    """
    Dichotomy Search

    :param pInterval: interval to search
    :param pMonotonicity: monotonicity (incremental or decremental)
    :param pAimVal: aim value
    :param pFunc: function to set condition or get value
    :return: result closest to pAimVal
    """
    low = pInterval[0]
    high = pInterval[1]
    closest = None
    mid_diff = float('inf')
    while low <= high:
        mid = (low + high) // 2
        realVal = pFunc(mid)
        diff = abs(realVal - pAimVal)

        if diff < mid_diff:
            mid_diff = diff
            closest = mid
        if pMonotonicity == 'incremental':
            if realVal < pAimVal:
                low = mid + 1
            elif realVal > pAimVal:
                high = mid - 1
            else:
                closest = mid
                break
        elif pMonotonicity == 'decremental':
            if realVal > pAimVal:
                low = mid + 1
            elif realVal < pAimVal:
                high = mid - 1
            else:
                closest = mid
                break
    return closest


def set_refubf(pHid, pDeviceAdd, pFlag):
    """
        set external or internal Vref
        :param pHid: hid object
        :param pDeviceAdd: device slave address
        :param pFlag: 0 external Vref, 1 internal Vref
        :return: PI_OK or PI_ERR
        """
    reg_temp = int(pi20_i2c_read(pHid, pDeviceAdd, 0x01, 0x0F), 16) & 0x00FD
    reg_target = 0
    if pFlag == 1:
        pi20_i2c_write(pHid, pDeviceAdd, 0x01, 0x0F, (pFlag << 1) | reg_temp)
        reg_target = (pFlag << 1) | reg_temp
    elif pFlag == 0:
        pi20_i2c_write(pHid, pDeviceAdd, 0x01, 0x0F, reg_temp)
        reg_target = (pFlag << 1) | reg_temp
    flag = int(pi20_i2c_read(pHid, pDeviceAdd, 0x01, 0x0F), 16)
    print("%04X" % flag)
    if flag == reg_target:
        return PI_OK
    else:
        return PI_ERR


