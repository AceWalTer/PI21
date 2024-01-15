# -*- encoding: utf-8 -*-
"""
    @File : adc_test.py \n
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


def adc_config(pHid, pDeviceAdd, pCH, pADCRange):
    pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x32, 0x000F)
    pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x33, 0x0089)
    if pADCRange == 1:
        pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x00, 0x03C0 + pCH)
    else:
        pi20_i2c_write(pHid, pDeviceAdd, 0x03, 0x00, 0x03D0 + pCH)


def adc_read(pHid, pDeviceAdd, pCH):
    val = pi20_i2c_read(pHid, pDeviceAdd, 0x04, pCH)
    return val
