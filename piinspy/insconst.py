# -*- encoding: utf-8 -*-
"""
    @File : insconst.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/11/23 10:25 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/11/23 10:25 \n
"""
ins_all_dict = {"POWER": ["6030", "821A", "831A"], "DMM": ["9060", "9061", "34461"], "LOAD": ["3021"],
                "MSO": ["MSO44"], "SMU": ["2450"]}

ins_sn_dict = {
    "POWER":
        {"6030": ["GEV860805", "GEW912502"],
         "821A": ["DP8E242000223"],
         "831A": ["DP8A242400223"]},

    "DMM":
        {"9061": ["GEV860805", "GEW912502"],
         "9060": [],
         "34461A": []},
    "LOAD":
        {"3021": ["DL3B245100577"]},
    "MSO":
        {"MSO44": []},
    "SMU":
        {"2450": ["4576516"],
         "2460": ["4624797"]}
}
