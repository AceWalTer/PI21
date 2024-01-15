# 这是一个示例 Python 脚本。
import time

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

from piinspy import *
# import xlwings as xw
import pyvisa
from utility import *
from buck_test import *
from nrail_test import *
from tec_test import *
from debug_test import *
from adc_test import *


def smu_sourceV_senseI(pIrange):
    smu.smu_reset()
    smu.write_cmd(":ROUT:TERM REAR")
    smu.smu_setsourfunc("VOLT")
    smu.smu_setsourceval("VOLT", 1.2)
    smu.smu_setsourcelimit("VOLT", "ILIMIT", 0.2)
    smu.smu_setsourcerange("VOLT", "AUTO ON")
    smu.smu_setsensefunc("\"CURR\"")
    smu.smu_setsenserange("CURR", pIrange)
    smu.smu_setsensenplc("CURR", 1)



def smu_enable(pFlag):
    if pFlag is True:
        smu.smu_setOutState("ON")
    else:
        smu.smu_setOutState("OFF")


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    # device_reset(pBdg, pAddr)
    pi_err_check(device_unlock(pBdg, pAddr))
    pi_err_check(check_device_id(pBdg, pAddr))
    pi_err_check(buck_freq_trim(pBdg, pAddr, 0x0780))  # 2MHz 0F8C 4MHz 0780
    ''' ************************ buck test area ********************************** '''
    # buck_range_test(buck_range_test_result_path, 0, 0.05)
    # buck_load_regulation_test(buck_load_regulation_result_path, 0, 0.05)
    # buck_load_test(buck_load_regulation_result_path, 1, 0.05)
    ''' ************************ NRAIL test area ********************************** '''
    # nrail_range_test(Nrail_range_test_result_path, 0, 0.05)
    # nrail_load_regulation_test(Nrail_load_regulation_test_result_path, 1, 0.05)
    ''' ************************ TEC test area ********************************** '''
    # tec_config(pBdg, pAddr, 0x0003)
    # set_tec_duty_cycle_manually(pBdg, pAddr, 0x1000)
    # set_tec_output_volt(pBdg, pAddr, 3, dmmVout, 1)
    ''' ************************ TIA test area ********************************** '''

    ''' ************************ debug test area ********************************** '''
    # fb_buck_source_vol_test()
    # USB0::0x05E6::0x2450::04576516::INSTR
    # smu = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2460::04624797::INSTR")
    smu = PiIns(rm, "SMU", "2450", "USB0::0x05E6::0x2450::04576516::INSTR")
    set_relay_multi(pBdg, [3, 8], "ON")
    smu_sourceV_senseI("10E-1")
    app = xw.App(visible=True, add_book=False)
    wb = app.books.open(r"D:\testrecord\PI20\idac\idac_sheet.xlsx")
    sheet = wb.sheets[3]
    # buck_enable(pBdg, pAddr, True)
    # set_buck_output_code(pBdg, pAddr, 0x0B85)
    start_time = time.time()

    pi20_i2c_write(pBdg, pAddr, 0x01, 0x02, 0x0002)
    smu_enable(True)
    code = [2048, 2049, 2050, 2051, 2052, 2053, 2054, 2055]
    code1 = [2048, 2056, 2064, 2072, 2080, 2088, 2096, 2104]
    code2 = range(2048, 4032 + 64, 64)
    code3 = range(0x0000, 0x0FFF + 0x0001, 0x0001)
    result = []
    iout = []
    for m in range(1):

        for n in code3:
            pi20_i2c_write(pBdg, pAddr, 0x02, 0x01, n)
            time.sleep(0.01)
            iout.append(smu.smu_ins_read())
        # result.append(iout)

    # print(result)

    sheet["b2"].options(transpose=True).value = iout
    sheet["a2"].options(transpose=True).value = code3
    sheet.api.Cells.HorizontalAlignment = -4108
    sheet.api.Cells.VerticalAlignment = -4108
    sheet.autofit("columns")
    wb.save()
    wb.close()
    app.quit()
    end_time = time.time()
    total_time = end_time - start_time
    print("Total runtime:", total_time, "seconds")
    # code 175.125 S
    # code1 175.282 S
    # code2 700,117 S
