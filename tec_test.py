# -*- encoding: utf-8 -*-
"""
    @File : tec_test.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/30 15:45 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/30 15:45 \n
"""
from utility import *
from piinspy import *
import numpy as np

dmmVout = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEW912502::INSTR")
dmmVout.dmm_setmode("VOLT", "DC")
dmmVout.dmm_setsamp(1)
dmmVout.dmm_settrig("IMM")


def tec_config(pHid, pDeviceAdd, cfg_code):
    """
    This function is used to configure the TEC
    :param pHid: Hid object
    :param pDeviceAdd: i2c slave address
    :param cfg_code: reg code for config TEC
    :return:  PI_OK or PI_ERR
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x08, 0x07, cfg_code)
    if pi20_i2c_read(pHid, pDeviceAdd, 0x08, 0x07) == "%04X" % cfg_code:
        return PI_OK
    else:
        return PI_ERR


def set_tec_duty_cycle_manually(pHid, pDeviceAdd, duty_cycle):
    """
    This function is used to set the TEC duty cycle
    :param pHid: Hid object
    :param pDeviceAdd: i2c slave address
    :param duty_cycle: duty cycle value code for TEC
    :return:  PI_OK or PI_ERR
    """
    pi20_i2c_write(pHid, pDeviceAdd, 0x08, 0x08, duty_cycle)


def set_tec_output_volt(pHid, pDeviceAdd, output_volt, pInsTecVolt, pDir):
    """
    This function is used to set the TEC output voltage
    :param pHid: hid object
    :param pDeviceAdd: i2c slave address
    :param output_volt: TEC output voltage
    :param pInsTecVolt: PiIns object for TEC output measure
    :param pDir: direction of TEC output voltage
    :return: None
    """
    if pDir == 1:
        set_tec_duty_cycle_manually(pHid, pDeviceAdd, 0x0000)
        stepsize = 0x1000
        code = 0x0000
        while True:
            set_tec_duty_cycle_manually(pHid, pDeviceAdd, code)
            vout = dmmVout.dmm_ins_read()
            if vout > output_volt:
                code -= stepsize
                if code <= 0x0000:
                    code = 0x0000
                stepsize = int(stepsize/4)
            else:
                code += stepsize
                if code >= 0x7FFF:
                    code = 0x7FFF
            if abs(output_volt - vout) <= 0.05:
                break

    elif pDir == 0:
        set_tec_duty_cycle_manually(pHid, pDeviceAdd, 0xFFFF)
        stepsize = 0x1000
        code = 0xFFFF
        while True:
            set_tec_duty_cycle_manually(pHid, pDeviceAdd, code)
            vout = dmmVout.dmm_ins_read()
            if vout < output_volt:
                code += stepsize
                if code >= 0xFFFF:
                    code = 0xFFFF
                stepsize = int(stepsize/4)
            else:
                code -= stepsize
                if code <= 0x8000:
                    code = 0x8000
            print(code)
            if abs(output_volt - vout) <= 0.05:
                break


def tec_load_test(pPath, pSheetNum, pSleepTime):
    """
    This function is used to test TEC when added load to tec and result is efficiency
    :param pPath: path of result document
    :param pSheetNum: sheet number
    :param pSleepTime: delay time
    :return: None
    """
    # init output voltage
    tec_vout = []
