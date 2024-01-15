# -*- encoding: utf-8 -*-
"""
    @File : ins_class.py \n
    @Contact : yafei.wang@pisemi.com \n
    @License : (C)Copyright {} \n
    @Modify Time : 2023/12/27 13:41 \n
    @Author : Pisemi Yafei Wang \n
    @Version : 1.0 \n
    @Description : None \n
    @Create Time : 2023/12/27 13:41 \n
"""
import time
from functools import wraps
from .ins_function import *


class PiIns:

    def __init__(self, prm, pInsType, pInsName, pInsID):
        self.pInsType = pInsType
        self.pInsName = pInsName
        self.pInsID = pInsID
        # self.pInsPort = ins_scan(prm, pInsType, pInsName)
        self.command = register_function(self.pInsType, self.pInsName)
        self.ins = prm.open_resource(self.pInsID)
        self.ins.timeout = 5000

    def __str__(self):
        return self.pInsType + " " + self.pInsName + " " + self.pInsID

    def write_cmd(self, pStr):
        print(self.ins.write(pStr))

    def query_cmd(self, pStr):
        print(self.ins.query(pStr))

    """************************** POWER FUNCs **************************************************"""

    def __power_funcs_permission(pFunc):
        @wraps(pFunc)
        def wrapper(self, *args, **kwargs):
            if self.pInsType == "POWER":
                return pFunc(self, *args, **kwargs)
            else:
                print("This is not a power instrument")

        return wrapper

    @__power_funcs_permission
    def power_setVol(self, pCh, pVolt):
        """
        set power supplies output voltage
        :param pCh: power channel
        :param pVolt: power output voltage
        :return: None
        """
        self.ins.write(self.command["setchvol"].format(CH=pCh, VOLT=pVolt))

    @__power_funcs_permission
    def power_setCur(self, pCh, pCurr):
        """
        set power supplies limit current
        :param pCh: power channel
        :param pCurr: power limit current
        :return: None
        """
        self.ins.write(self.command["setchcur"].format(CH=pCh, CURR=pCurr))

    @__power_funcs_permission
    def power_setOutState(self, pCh, pState):
        """
        set power output state
        :param pCh: power channel
        :param pState:power output state
        :return: None
        """
        if self.pInsName == "831A" or self.pInsName == "821A":
            ch = "CH%d" % pCh
        else:
            ch = pCh
        time.sleep(0.5)
        self.ins.write(self.command["outputstate"].format(CH=ch, STATE=pState))

    @__power_funcs_permission
    def power_reset(self):
        """
        reset power supplies
        :return: None
        """
        time.sleep(0.5)
        self.ins.write(self.command["reset"])
        pass

    @__power_funcs_permission
    def power_measure(self, pType, pCh):
        """
        measure power supplies output voltage, current or power
        :param pType: measure type (VOLT, CURR, POWER)
        :param pCh: measure channel
        :return: measure val
        """
        val = float(self.ins.query(self.command["measure"].format(TYPE=pType, CH=pCh)))
        return val

    """************************** DMM FUNCs **************************************************"""
    def __dmm_funcs_permission(pFunc):
        @wraps(pFunc)
        def wrapper(self, *args, **kwargs):
            if self.pInsType == "DMM":
                return pFunc(self, *args, **kwargs)
            else:
                print("This is not a dmm instrument")

        return wrapper

    @__dmm_funcs_permission
    def dmm_setmode(self, pMode, pType):
        """
        set dmm mode
        :param pMode: dmm mode(VOLT or CURR)
        :param pType: dmm mode type(AC or DC)
        :return: None
        """
        if pMode == "VOLT" or pMode == "CURR":
            self.ins.write(self.command["conf"].format(MODE=pMode, TYPE=pType))
        else:
            self.ins.write(self.command["conf"][:11].format(MODE=pMode))

    @__dmm_funcs_permission
    def dmm_setsamp(self, pCount):
        """
        set dmm samp
        :param pCount: dmm samp count
        :return: None
        """
        self.ins.write(self.command["samp"].format(COUNT=pCount))

    @__dmm_funcs_permission
    def dmm_setrange(self, pMode, pType, pVal):
        """
        set dmm range
        :param pMode: dmm mode(VOLT or CURR)
        :param pType: dmm type(AC or DC)
        :param pVal: dmm range value
        :return: None
        """
        self.ins.write(self.command["range"].format(MODE=pMode, TYPE=pType, RANGE=pVal))

    @__dmm_funcs_permission
    def dmm_settrig(self, pTrig):
        """
        set dmm trig
        :param pTrig: dmm trig type
        :return: None
        """
        self.ins.write(self.command["trig"].format(TRIG=pTrig))

    @__dmm_funcs_permission
    def dmm_ins_read(self):
        """
        read dmm value
        :return: dmm value
        """
        val = float(self.ins.query(self.command["read"]))
        return val

    """************************** SMU FUNCs **************************************************"""

    def __smu_funcs_permission(pFunc):
        @wraps(pFunc)
        def wrapper(self, *args, **kwargs):
            if self.pInsType == "SMU":
                return pFunc(self, *args, **kwargs)
            else:
                print("This is not a smu instrument")

        return wrapper

    @__smu_funcs_permission
    def smu_setsourfunc(self, pSourFunc):
        """
        set smu source type(VOLT or CURR)
        :param pSourFunc: source type(VOLT or CURR)
        :return: None
        """
        self.ins.write(self.command["sourfunc"].format(TYPE=pSourFunc))

    @__smu_funcs_permission
    def smu_setsourceval(self, pType, pVal):
        """
        set smu source value
        :param pType: source type(VOLT or CURR)
        :param pVal: source value
        :return: None
        """
        self.ins.write(self.command["soursetval"].format(TYPE=pType, VAL=pVal))

    @__smu_funcs_permission
    def smu_setsourcelimit(self, pType, pLimit, pVal):
        """
        set smu source limit(ILIMIT or VLIMIT) value
        :param pType: source type(VOLT or CURR)
        :param pLimit: source limit(ILIMIT or VLIMIT)
        :param pVal: Limit value
        :return: None
        """
        self.ins.write(self.command["soursetlimit"].format(TYPE=pType, LIMIT=pLimit, VAL=pVal))

    @__smu_funcs_permission
    def smu_setsourcerange(self, pType, pRange):
        """
        set smu source range
        :param pType: source type(VOLT or CURR)
        :param pRange: source range
        :return: None
        """
        self.ins.write(self.command["soursetrange"].format(TYPE=pType, RANGE=pRange))

    @__smu_funcs_permission
    def smu_setsensefunc(self, pSenseFunc):
        """
        set smu sense type(VOLT or CURR)
        :param pSenseFunc: sense type(VOLT or CURR)
        :return: None
        """
        self.ins.write(self.command["sensefunc"].format(TYPE=pSenseFunc))

    @__smu_funcs_permission
    def smu_setsenserange(self, pType, pRange):
        """
        set smu sense range
        :param pType: sense type(VOLT or CURR)
        :param pRange: sense range
        :return:
        """
        if "AUTO" in pRange:
            self.ins.write(self.command["sensesetrange"].format(TYPE=pType, RANGE=pRange))
        else:
            self.ins.write(self.command["sensesetrange"][:17].format(TYPE=pType) + " "+pRange)

    @__smu_funcs_permission
    def smu_setsensenplc(self, pType, pVal):
        """
        set sense NPLC value
        :param pType: sense type(VOLT or CURR)
        :param pVal: NPLC value
        :return: None
        """
        self.ins.write(self.command["sensesetnplc"].format(TYPE=pType, VAL=pVal))

    @__smu_funcs_permission
    def smu_setOutState(self, pState):
        """
        set smu output state
        :param pState: output state
        :return: None
        """
        time.sleep(0.5)
        self.ins.write(self.command["outputstate"].format(STATE=pState))

    @__smu_funcs_permission
    def smu_reset(self):
        """
        smu reset
        :return: None
        """
        self.ins.write(self.command["reset"])

    @__smu_funcs_permission
    def smu_ins_read(self):
        """
        Read smu sense value
        :return: smu sense value
        """
        val = float(self.ins.query(self.command["read"]))
        return val

    """************************** LOAD FUNCs **************************************************"""
    def __load_funcs_permission(pFunc):
        @wraps(pFunc)
        def wrapper(self, *args, **kwargs):
            if self.pInsType == "LOAD":
                return pFunc(self, *args, **kwargs)
            else:
                print("This is not a smu instrument")

        return wrapper

    @__load_funcs_permission
    def load_setsourfunc(self, pSourFunc):
        """
        set source type(VOLT or CURR)
        :param pSourFunc: source type(VOLT or CURR)
        :return: None
        """
        self.ins.write(self.command["sourfunc"].format(TYPE=pSourFunc))

    @__load_funcs_permission
    def load_setsourcevolt(self, pType, pVal):
        """
        set voltage
        :param pType: source type
        :param pVal: source value
        :return: None
        """
        self.ins.write(self.command["sourcevolt"].format(TYPE=pType, VAL=pVal))

    @__load_funcs_permission
    def load_setinputstate(self, pState):
        """
        set load input state
        :param pState: load input state
        :return: None
        """
        self.ins.write(self.command["inputstate"].format(STATE=pState))
