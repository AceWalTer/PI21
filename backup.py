# -*- encoding: utf-8 -*-
"""
    @File : backup.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2024/1/8 13:20 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2024/1/8 13:20 \n
"""
# if abs(idac_cur_ofset - 0) < 0.00005:
#     reg_dict["IDAC_GAIN_B22A00_[7:0]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
#     value_dict["IDAC_0x0100"] = idac_cur_ofset
#     smu_enable(False)
#     set_relay_unit(pBdg, 0)
#     return trim_pass
# else:
#     for i in range(0x0000, 0x00FF + 0x0001, 0x0001):
#         pi20_i2c_write(pBdg, pAddr, 0x22, 0x00, (i << 8) | reg_temp)
#         idac_cur_ofset = -smu.smu_ins_read()
#         if abs(idac_cur_ofset - 0) < 0.00005:
#             reg_dict["IDAC_OFFSET_B22A00_[15:8]"] = pi20_i2c_read(pBdg, pAddr, 0x22, 0x00)
#             value_dict["IDAC_0x0100"] = idac_cur_ofset
#             smu_enable(False)
#             set_relay_unit(pBdg, 0)
#             return trim_pass