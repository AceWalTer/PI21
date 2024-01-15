import time


def hid_spi_write(pHidBdg, pData):
    """
    write function which convert hid into spi
    :param pHidBdg: hid object
    :param pData: write data. (note: list format)
    :return:
    """
    data = [0x1, len(pData)+5, 0x01, 0x11, 0x0, 0x0, len(pData)]
    data.extend(pData)
    pHidBdg.write(data)

def hid_spi_read(pHidBdg, pNum):
    """
    read function which convert hid into spi
    note: this function need to be updated!!!
          need add read register address,
          register address may be 1byte or 4 bytes,
          so need to judge register address length!!!
    :param pHidBdg: hid object
    :param pNum: read data number
    :return:
    """
    # data = [0x1, 3, 0x02, 0x11, pNum]
    return pHidBdg.read(pNum)


def i2c_write(pHidBdg, slaveAddr, i2cConf, dataList ):
    """
    i2c write function
    :param pHidBdg: hid object
    :param slaveAddr: slave address (7bit address)
    :param i2cConf: configure i2c speed
    :param dataList: write data (note: list format)
    :return:
    """
    data = [0x1, len(dataList) + 5, 0x01, 0x12, slaveAddr, i2cConf, len(dataList)]
    data.extend(dataList)
    pHidBdg.write(data)
    time.sleep(0.05)


def i2c_read(pHidBdg, slaveAddr, i2cConf, dataNum, regAddr):
    """
    i2c read function
    :param pHidBdg:hid object
    :param slaveAddr:
    :param i2cConf:
    :param dataNum:
    :param regAddr:
    :return:
    """
    # send read register address
    # data = [0x1, len(regAddr)+5, 0x02, 0x12, slaveAddr, i2cConf, dataNum]
    data = [0x1, len(hex(regAddr))-2 + 5, 0x02, 0x12, slaveAddr, i2cConf, dataNum]
    # data.extend(regAddr)
    data.append(regAddr)
    # data = [0x1, 1 + 5, 0x02, 0x12, slaveAddr, i2cConf, dataNum, regAddr]
    pHidBdg.write(data)
    time.sleep(0.05)
    # read data from hid device
    return pHidBdg.read(dataNum+1)


def gpio_write(pHidBdg, gpio_pin, gpio_data ):
    """
    GPIO write function
    :param pHidBdg: hid object
    :param gpio_pin: gpio pin number
                      0 - gpio0
                      1 - gpio1
                      2 - gpio2
                      3 - gpio3
                      ...
                      7 - gpio7
    :param gpio_data: gpio toggle value
                      0 - gpio output low
                      1 - gpio output high
    :return:
    """
    data = [0x1, len(gpio_data) + 5, 0x01, 0x80, gpio_pin, 0x00, len(gpio_data)]
    data.extend(gpio_data)
    pHidBdg.write(data)
    time.sleep(0.05)
