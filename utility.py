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
from subM_brig_ch32.pi20_drvier import *
import pyvisa
import xlwings as xw

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
# quit()

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
