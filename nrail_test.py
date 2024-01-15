# -*- encoding: utf-8 -*-
"""
    @File : nrail_test.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/27 16:56 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/27 16:56 \n
"""
from utility import *
from piinspy import *
import numpy as np

Nrail_range_test_result_path = r"D:\testrecord\PI20\NRAIL\NRAIL_range_test_result.xlsx"
Nrail_load_regulation_test_result_path = r"D:\testrecord\PI20\NRAIL\NRAIL_loade_regulation_test_result.xlsx"


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


def nrail_range_test(pPath, pSheetNum, pSleepTime):
    """
    NRAIL Range Test function
    :param pPath: path of result document
    :param pSheetNum: sheet number
    :param pSleepTime: delay time
    :return: None
    """
    # init output code
    code = list(range(0x0000, 0x001F, 0x0001))
    code.append(0x001F)

    # init excel
    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(pPath)
    sheet = wb.sheets[pSheetNum]
    xdata = ["Vref", "Vout", "ideal", "Delta"]
    ydata = []
    for i in code:
        ydata.append("%04X" % i)

    sheet["a4:a%d" % len(ydata)].api.NumberFormat = "@"
    write_data_to_excel(sheet, "b3", "a4", "b%d" % len(xdata), "a%d" % len(ydata), xdata, ydata)

    # init ins condition
    dmm_Vref = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEV860805::INSTR")
    dmm_Vout = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEW912502::INSTR")
    dmm_Vref.dmm_setmode("VOLT", "DC")
    dmm_Vref.dmm_setsamp(1)
    dmm_Vref.dmm_settrig("IMM")
    dmm_Vout.dmm_setmode("VOLT", "DC")
    dmm_Vout.dmm_setsamp(1)
    dmm_Vout.dmm_settrig("IMM")

    # init result data
    Vref_data = []
    Vout_data = []
    ideal_data = []
    delta_data = []

    # test sequence

    nrail_enable(pBdg, pAddr, True)

    for output_code in code:
        set_nrail_output_code(pBdg, pAddr, output_code)
        time.sleep(pSleepTime)
        vref = dmm_Vref.dmm_ins_read()
        vout = dmm_Vout.dmm_ins_read()
        ideal = -vref * (output_code * 0.04 + 0.76)
        Vref_data.append(vref)
        Vout_data.append(vout)
        ideal_data.append(ideal)
        delta_data.append(vout - ideal)

    write_data_to_excel(sheet, "b4", "b4", "b4", "b%d" % len(ydata), 0, Vref_data)
    write_data_to_excel(sheet, "c4", "c4", "c4", "c%d" % len(ydata), 0, Vout_data)
    write_data_to_excel(sheet, "d4", "d4", "d4", "d%d" % len(ydata), 0, ideal_data)
    write_data_to_excel(sheet, "e4", "e4", "e4", "e%d" % len(ydata), 0, delta_data)

    sheet.api.Cells.HorizontalAlignment = -4108
    sheet.api.Cells.VerticalAlignment = -4108
    sheet.autofit("columns")
    wb.save()
    wb.close()
    app.quit()


def nrail_load_regulation_test(pPath, pSheetNum, pSleepTime):
    pass
    # init output code
    code = [0x0001, 0x0006, 0x000E, 0x0015, 0x001F]

    # init excel
    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(pPath)
    sheet = wb.sheets[pSheetNum]
    # load_cur = list(range(0, 500, 100))
    load_cur = np.arange(0.00, 0.12, 0.02).tolist()
    xdata = load_cur
    ydata = ["0001", "Vref", "Opow", "PVDD", "Ppow",
             "0006", "Vref", "Opow", "PVDD", "Ppow",
             "000E", "Vref", "Opow", "PVDD", "Ppow",
             "0015", "Vref", "Opow", "PVDD", "Ppow",
             "001F", "Vref", "Opow", "PVDD", "Ppow"]

    sheet["a4:a%d" % len(ydata)].api.NumberFormat = "@"
    write_data_to_excel(sheet, "b3", "a4", "b%d" % len(xdata), "a%d" % len(ydata), xdata, ydata)

    # init ins condition
    dmm_Vref = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEV860805::INSTR")
    dmm_Vout = PiIns(rm, "DMM", "9061", "USB0::0x2184::0x0059::GEW912502::INSTR")
    dmm_Vref.dmm_setmode("VOLT", "DC")
    dmm_Vref.dmm_setsamp(1)
    dmm_Vref.dmm_settrig("IMM")
    dmm_Vout.dmm_setmode("VOLT", "DC")
    dmm_Vout.dmm_setsamp(1)
    dmm_Vout.dmm_settrig("IMM")

    smu_load = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2460::04624797::INSTR")
    smu_load.smu_reset()
    smu_load.smu_setsourfunc("CURR")
    smu_load.smu_setsourceval("CURR", 0)
    smu_load.smu_setsourcelimit("CURR", "VLIMIT", 6)
    smu_load.smu_setsourcerange("CURR", "AUTO ON")
    smu_load.smu_setsensefunc("\"VOLT\"")
    smu_load.smu_setsenserange("VOLT", "AUTO ON")
    smu_load.smu_setsensenplc("VOLT", 1)

    power821A = PiIns(rm, "POWER", "821A", "USB0::0x1AB1::0x0E11::DP8E242000223::INSTR")

    # init result data
    Vref_data = []
    Vout_data = []
    opow_data = []
    pvdd_data = []
    ppow_data = []
    # test sequence

    nrail_enable(pBdg, pAddr, True)
    set_nrail_output_code(pBdg, pAddr, 0x00001)
    print(dmm_Vout.dmm_ins_read())
    smu_load.smu_setOutState("ON")
    pos_num = 4
    for i in code:
        set_nrail_output_code(pBdg, pAddr, i)
        time.sleep(pSleepTime)

        for j in load_cur:
            smu_load.smu_setsourceval("CURR", j)
            time.sleep(pSleepTime)
            vref = dmm_Vref.dmm_ins_read()
            time.sleep(pSleepTime)
            vout = dmm_Vout.dmm_ins_read()
            time.sleep(pSleepTime)
            opow = j*vout
            pvdd = power821A.power_measure("VOLT", 2)
            time.sleep(pSleepTime)
            ppow = power821A.power_measure("POWER", 2)
            time.sleep(pSleepTime)
            Vref_data.append(vref)
            Vout_data.append(vout)
            opow_data.append(opow)
            pvdd_data.append(pvdd)
            ppow_data.append(ppow)

        write_data_to_excel(sheet, "b%d" % pos_num, "b%d" % pos_num, "g%d" % len(xdata),
                            "b%d" % pos_num, Vout_data, 0)

        write_data_to_excel(sheet, "b%d" % (pos_num + 1), "b%d" % (pos_num + 1), "g%d" % len(xdata),
                            "b%d" % (pos_num + 1), Vref_data, 0)

        write_data_to_excel(sheet, "b%d" % (pos_num + 2), "b%d" % (pos_num + 2), "g%d" % len(xdata),
                            "b%d" % (pos_num + 2), opow_data, 0)

        write_data_to_excel(sheet, "b%d" % (pos_num + 3), "b%d" % (pos_num + 3), "g%d" % len(xdata),
                            "b%d" % (pos_num + 3), pvdd_data, 0)

        write_data_to_excel(sheet, "b%d" % (pos_num + 4), "b%d" % (pos_num + 4), "g%d" % len(xdata),
                            "b%d" % (pos_num + 4), ppow_data, 0)
        pos_num += 5
        Vref_data.clear()
        Vout_data.clear()
        opow_data.clear()
        pvdd_data.clear()
        ppow_data.clear()
        smu_load.smu_setsourceval("CURR", 0)

    smu_load.smu_setOutState("OFF")
    sheet.api.Cells.HorizontalAlignment = -4108
    sheet.api.Cells.VerticalAlignment = -4108
    sheet.autofit("columns")
    wb.save()
    wb.close()
    app.quit()