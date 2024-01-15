# -*- encoding: utf-8 -*-
"""
    @File : ins_function.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/11/20 10:04 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/11/20 10:04 \n
"""

import json
import os
import pyvisa
import time
from piinspy import insconst


def register_function(pInsType, pInsName):
    """
    register the instrument function
    :param pInsType: instrument type
    :param pInsName: instrument name
    :return: command
    """

    # Get the path of the current file
    current_file = os.path.realpath(__file__)

    # Get the directory containing the current file
    current_dir = os.path.dirname(current_file)

    # Construct the path to the JSON file
    json_file = os.path.join(current_dir, 'ins.json')

    # Read and parse the JSON file
    with open(json_file, 'r') as f:
        command = json.load(f)

    for i in command.keys():
        if pInsType == i:
            for j in command[i].keys():
                if pInsName[:3] in j:
                    print(command[i][j])
                    return command[i][j]


def ins_scan(pInsrm):
    """
    scan the instrument automatically
    :param pInsrm: pyvsia object
    :return: instrument class, name and port dict
    """
    ins_visa_dict = {}
    for i in pInsrm.list_resources():
        ''' ::0:: unconnected ins ASRL3,ASEL4 Bluetooth COM ports '''

        if "::0::" in i or "ASRL3::INSTR" in i or "ASRL4::INSTR" in i:
            pass
        else:
            ins = pInsrm.open_resource(i)
            ins.read_termination = "\n"
            ins.timeout = 2000
            try:
                ins_info = ins.query("*IDN?")
                for k in insconst.ins_all_dict:
                    for j in insconst.ins_all_dict[str(k)]:
                        if j in str(ins_info):

                            print(k, j, i, ins_info)
                            ins_visa_dict.update({i: {k: j}})

                ins.close()
            except Exception as result:
                print(result)
    print(ins_visa_dict)
