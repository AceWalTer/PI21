# -*- encoding: utf-8 -*-
"""
    @File : debug_test.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/30 15:11 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/30 15:11 \n
"""
from utility import *
from piinspy import *
import numpy as np


def fb_buck_source_vol_test():
    """
    This function used to source voltage to buck converter FB_BUCK PIN and measure Vref.
    :return: None
    """
    # init source vol
    vol = np.arange(0, 2.5, 0.5).tolist()

    #  init condition
    dmm_Vref = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEV860805::INSTR")
    dmm_Vref.dmm_setmode("VOLT", "DC")
    dmm_Vref.dmm_setsamp(1)
    dmm_Vref.dmm_settrig("IMM")
    dmm_Vref.dmm_setsamp(1)
    dmm_Vref.dmm_settrig("IMM")

    smu_load = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2460::04624797::INSTR")
    smu_load.smu_reset()
    smu_load.smu_setsourfunc("VOLT")
    smu_load.smu_setsourceval("VOLT", 0)
    smu_load.smu_setsourcelimit("VOLT", "ILIMIT", 0.1)
    smu_load.smu_setsourcerange("VOLT", "AUTO ON")
    smu_load.smu_setsensefunc("\"CURR\"")
    smu_load.smu_setsenserange("CURR", "AUTO ON")
    smu_load.smu_setsensenplc("CURR", 1)
    smu_load.smu_setOutState("ON")
    for i in vol:
        smu_load.smu_setsourceval("VOLT", i)
        print(dmm_Vref.dmm_ins_read())

