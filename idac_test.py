# -*- encoding: utf-8 -*-
"""
    @File : idac_test.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/25 14:15 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/25 14:15 \n
"""
import time

from utility import *
from piinspy import *

def idac_config():
    """
    IDAC Settings function
    :return:
    """
    pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0000)
    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0002)


def idac_liner_test():
    """
    Test IDAC output and input code slope with different scale trim
    :return: None
    """

    #  unlock
    pi20_i2c_write(pBdg, pAddr, 0x40, 0x00, 0xC0DE)
    pi20_i2c_write(pBdg, pAddr, 0x40, 0x01, 0xF00D)

    # idac enable
    idac_config()

    # trim code
    trim_code = [0x0000, 0x0080]
    output_code = [0x0000, 0x0100, 0x0400, 0x0800, 0x0C00, 0x0F00]

    # test result
    idac_cur = []

    # instruments config
    smu_idac_output = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2460::04624797::INSTR")

    for i in trim_code:
        pi20_i2c_write(pBdg, pAddr, 0x21, 0x00, i)
        pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, 0x0000)
        for j in output_code:
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, j)
            time.sleep(0.05)
            idac_cur.append(smu_idac_output.smu_ins_read())
