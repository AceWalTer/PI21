from subM_brig_ch32.IfDriver import *
import hid


def pi20_i2c_write(pHid, pSlaveAddr, pBlockAddr, pRegAddr, pData):
    i2c_write(pHid, pSlaveAddr, 0x00, [0x80, 0x00, pBlockAddr])
    i2c_write(pHid, pSlaveAddr, 0x00, [pRegAddr, (pData >> 8) & 0xFF, (pData & 0xFF)])


def pi20_i2c_read(pHid, pSlaveAddr, pBlockAddr, pRegAddr):
    i2c_write(pHid, pSlaveAddr, 0x00, [0x80, pBlockAddr, 0x00])
    rdData = i2c_read(pHid, pSlaveAddr, 0x00, 2, pRegAddr)
    hexData = [rdData[1], rdData[2]]
    counter = 0
    value_read = 0
    # print(hexData)
    for k in reversed(hexData):
        value_read += k << (8 * counter)
        counter += 1
    return "%04X" % value_read
    # return hexData


if __name__ == "__main__":
    """ test case """
    pBdg = hid.device()  # create hid device
    pBdg.open(0x1A86, 0xFE07)
    pAddr = 0x80
    print(pi20_i2c_read(pBdg, pAddr, 0x00, 0x01))
    # pi20_i2c_write(pBdg, pAddr, 0x0b, 0x00, 0x0001)
    # pi20_i2c_write(pBdg, pAddr, 0x0b, 0x01, 0x0b85)
    pBdg.close()
