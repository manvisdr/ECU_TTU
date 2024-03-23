from paho.mqtt import client as mqtt_client
import serial
import struct
from datetime import datetime
import json
import binascii
import time

POLYNOMIAL = 0x1021
PRESET = 0

loadFile = open('edmicmdDev.json', 'r')
edmiList = json.loads(loadFile.read())
buff_device_LV = edmiList[0]['list']
buff_device_MV = edmiList[1]['list']


# for i in range(0, len(edmiList[0])):
#     bu
# for i in edmiList:
#     serialList[counter] = i
#     counter += 1
# for v in i['list']:
#     print(v)
# print(serialList)
# print(i['list'])
#     for j in range():
#         serialList[i][j]= serial1.to_bytes(4, byteorder='big')
# serial1 = int(edmiList[0]['list'][0]['serialNumber'])
# serial1 = serial1.to_bytes(4, byteorder='big')


def crc16_xmodem(data: bytes):
    return binascii.crc_hqx(data, 0)


def int_to_bytes(val):
    data = []
    while val > 0:
        b = val % 256
        val = val // 256
        data.insert(0, b)
    return bytes(data)


def _initial(c):
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return crc


_tab = [_initial(i) for i in range(256)]


def _update_crc(crc, c):
    cc = 0xff & c

    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff
    # print(crc)

    return crc


def crc(str):
    crc = PRESET
    for c in str:
        crc = _update_crc(crc, ord(c))
    return crc


def crcb(*i):
    crc = PRESET
    for c in i:
        crc = _update_crc(crc, c)
    return crc


def bitwise_and_bytes(a, b):
    result_int = int.from_bytes(
        a, byteorder="big") & int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")


broker = '190.92.220.180'
port = 1883
client_id = f'asdasdfsfds'
username = 'das'
password = 'mgi2022'

NUL = b'\x00'  # NULL termination character
STX = b'\x02'  # START OF TEXT
ETX = b'\x03'  # END OF TEXT
EOT = b'\x04'  # END OF TRANSMISSION
ENQ = b'\x05'  # ASCII b'\x05 == ENQUIRY
ACK = b'\x06'  # ACKNOWLEDGE
LF = b'\x0A'  # LINE FEED \n
CR = b'\x0D'   # CARRIAGE RETURN \r
DLE = b'\x10'  # DATA LINE ESCAPE
XON = b'\x11'  # XON Resume transmission
XOFF = b'\x13'  # XOFF Pause transmission
CAN = b'\x18'  # CANCEL
R_FUNC = b'\x52'  # READ REGISTER
L_FUNC = b'\x4C'  # LOGIN REGISTER
E_FUNC = b'\x45'  # BROADCAST REGISTER

D_NUL = 0x00  # NULL termination character
D_STX = 0x02  # START OF TEXT
D_ETX = 0x03  # END OF TEXT
D_EOT = 0x04  # END OF TRANSMISSION
D_ENQ = 0x05  # ASCII b'\x05 == ENQUIRY
D_ACK = 0x06  # ACKNOWLEDGE
D_LF = 0x0A  # LINE FEED \n
D_CR = 0x0D   # CARRIAGE RETURN \r
D_DLE = 0x10  # DATA LINE ESCAPE
D_XON = 0x11  # XON Resume transmission
D_XOFF = 0x13  # XOFF Pause transmission
D_CAN = 0x18  # CANCEL
D_R_FUNC = 0x52  # READ REGISTER
D_L_FUNC = 0x4C  # LOGIN REGISTER
D_E_FUNC = 0x45  # BROADCAST REGISTER

REG_INSTAN_VOLTR = [0x52, 0xE0, 0x00]  # VOLTAGE PHASE A
REG_INSTAN_VOLTS = [0x52, 0xE0, 0x01]  # VOLTAGE PHASE B
REG_INSTAN_VOLTT = [0x52, 0xE0, 0x02]  # VOLTAGE PHASE C
REG_INSTAN_CURRR = [0x52, 0xE0, 0x10]  # CURRENT PHASE A
REG_INSTAN_CURRS = [0x52, 0xE0, 0x11]  # CURRENT PHASE B
REG_INSTAN_CURRT = [0x52, 0xE0, 0x12]  # CURRENT PHASE C
REG_INSTAN_WATTR = [0x52, 0xE0, 0x30]  # WATT PHASE A
REG_INSTAN_WATTS = [0x52, 0xE0, 0x31]  # WATT PHASE B
REG_INSTAN_WATTT = [0x52, 0xE0, 0x32]  # WATT PHASE C
REG_INSTAN_PFACT = [0x52, 0xE0, 0x26]  # POWER FACTOR
REG_INSTAN_FREQU = [0x52, 0xE0, 0x60]  # FREQUENCY
REG_ENERGY_KVARH = [0x52, 0x1E, 0x20]  # TOU ENERGY KVARH
REG_ENERGY_KWHLBP = [0x52, 0x1E, 0x01]  # TOU ENERGY
REG_ENERGY_KWHBP = [0x52, 0x1E, 0x02]
REG_ENERGY_KWHTOT = [0x52, 0x1E, 0x00]
REG_SERIAL_NUMBER = [0x52, 0xF0, 0x02]
BROADCAST_RECEIVE = [b'\xff', b'\xff', b'\xff', b'\xfe']

register_mk10 = [
    [0x52, 0xE0, 0x00],  # VOLTAGE PHASE A
    [0x52, 0xE0, 0x01],  # VOLTAGE PHASE B
    [0x52, 0xE0, 0x02],  # VOLTAGE PHASE C
    [0x52, 0xE0, 0x10],  # CURRENT PHASE A
    [0x52, 0xE0, 0x11],  # CURRENT PHASE B
    [0x52, 0xE0, 0x12],  # CURRENT PHASE C
    [0x52, 0xE0, 0x30],  # WATT PHASE A
    [0x52, 0xE0, 0x31],  # WATT PHASE B
    [0x52, 0xE0, 0x32],  # WATT PHASE C
    [0x52, 0xE0, 0x26],  # POWER FACTOR
    [0x52, 0xE0, 0x60],  # FREQUENCY
    [0x52, 0x1E, 0x20],  # KVARH
    [0x52, 0x1E, 0x02],  # KWH WBP
    [0x52, 0x1E, 0x01],  # KWH LWBP
    [0x52, 0x1E, 0x00]   # KWH TOTAL
]


register_mk6n = [
    [0x52, 0xE0, 0x00],  # VOLTAGE PHASE A
    [0x52, 0xE0, 0x01],  # VOLTAGE PHASE B
    [0x52, 0xE0, 0x02],  # VOLTAGE PHASE C
    [0x52, 0xE0, 0x10],  # CURRENT PHASE A
    [0x52, 0xE0, 0x11],  # CURRENT PHASE B
    [0x52, 0xE0, 0x12],  # CURRENT PHASE C
    [0x52, 0xE0, 0x30],  # WATT PHASE A
    [0x52, 0xE0, 0x31],  # WATT PHASE B
    [0x52, 0xE0, 0x32],  # WATT PHASE C
    [0x52, 0xE0, 0x26],  # POWER FACTOR
    [0x52, 0xE0, 0x60],  # FREQUENCY
    [0x52, 0x03, 0x69],  # KVARH
    [0x52, 0x01, 0x60],  # KWH WBP
    [0x52, 0x01, 0x61],  # KWH LWBP
    [0x52, 0x01, 0x69]   # KWH TOTAL
]

name_all_register = ["voltR", "voltS", "voltT", "currR", "currS", "currT",
                     "wattR", "wattS", "wattT", "pf", "freq", 'kvarh', "kwhBP", "kwhLBP", "kwhtotal"]


class EdmiReader:
    def __init__(self, port, baud):
        self.serial = serial.Serial(port)
        self.serial.baudrate = baud
        self.serial.timeout = 1

    def TX_raw(self, ch):
        self.serial.write(bytes(ch))
        # self.serial.flush()

    def TX_byte(self, d):
        if d == 0x02:  # STX
            # print("STX")
            self.TX_raw(DLE)
            d = d | 0x40
            self.TX_raw(d.to_bytes(1, 'big'))
        elif d == 0x03:  # ETX
            # print("ETX")
            self.TX_raw(DLE)
            d = d | 0x40
            self.TX_raw(d.to_bytes(1, 'big'))
        elif d == 0x10:  # DLE
            # print("DLE")
            self.TX_raw(DLE)
            d = d | 0x40
            self.TX_raw(d.to_bytes(1, 'big'))
        elif d == 0x11:  # XON
            # print("XON")
            self.TX_raw(DLE)
            d = d | 0x40
            self.TX_raw(d.to_bytes(1, 'big'))
        elif d == 0x13:  # XOFF
            # print("XOFF")
            self.TX_raw(DLE)
            d = d | 0x40
            self.TX_raw(d.to_bytes(1, 'big'))
        else:
            if type(d) == bytes:
                self.TX_raw(d)
            else:
                self.TX_raw(d.to_bytes(1, 'big'))

    def TX_cmd(self, cmd):
        self.TX_raw(STX)
        # crc = CalculateCharacterCRC16(0, STX)
        stx = int.from_bytes(STX, byteorder='big')
        crc = _update_crc(0, stx)

        for i in range(len(cmd)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            self.TX_byte(cmd[i])
            crc = _update_crc(crc, cmd[i])

        self.TX_byte(crc.to_bytes(2, 'big'))
        self.TX_raw(ETX)

    def read(self):

        while (True):
            # Check if incoming bytes are waiting to be read from the serial input
            # buffer.
            # NB: for PySerial v3.0 or later, use property `in_waiting` instead of
            # function `inWaiting()` below!
            if (self.serial.inWaiting() > 0):
                # read the bytes and convert from binary array to ASCII
                data_str = self.serial.read(
                    self.serial.inWaiting())
                # print the incoming string without putting a new-line
                # ('\n') automatically after every print()
                print(data_str)

            # Put the rest of your code you want here

            # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let
            # other threads on your PC run during this time.
            time.sleep(0.01)

    def read2(self):
        counter = 0
        dlechar = False
        message = []
        index = 0
        completeMsg = False
        while True:
            # if (self.serial.inWaiting() > 0):
            inChar = self.serial.read()
            # if completeMsg:
            #     break
            if inChar == STX:
                while True:
                    inChar = self.serial.read()
                    # print(inChar)
                    if inChar != ETX:
                        if (inChar == DLE):
                            dlechar = True
                        else:
                            if (dlechar):
                                inChar = bitwise_and_bytes(inChar, b'\xBF')
                            dlechar = False
                            message.append(inChar)
                            index += 1
                    else:
                        print("completeMsg")
                        completeMsg = True
                        break

        # else:
            if completeMsg:
                break
        return message

    def login(self):
        login = [0x02, 0x4C, 0x45, 0x44, 0x4D, 0x49, 0x2C, 0x49, 0x4D,
                 0x44, 0x45, 0x49, 0x4D, 0x44, 0x45, 0x00, 0xD9, 0x69, 0x03]
        self.serial.write(bytearray(login))
        ret_login = self.read2()
        print(ret_login)
        # continues = False
        # if ret_login[0] == ACK and ret_login[1] == ACK:
        #     continues = True
        #     print("login accepted")
        # if not continues:
        #     print("login not accepted")
        #     continues = False
        # return continues


def ieee_754_conversion(n, sgn_len=1, exp_len=8, mant_len=23):
    """
    Converts an arbitrary precision Floating Point number.
    Note: Since the calculations made by python inherently use floats, the accuracy is poor at high precision.
    :param n: An unsigned integer of length `sgn_len` + `exp_len` + `mant_len` to be decoded as a float
    :param sgn_len: number of sign bits
    :param exp_len: number of exponent bits
    :param mant_len: number of mantissa bits
    :return: IEEE 754 Floating Point representation of the number `n`
    """
    if n >= 2 ** (sgn_len + exp_len + mant_len):
        raise ValueError(
            "Number n is longer than prescribed parameters allows")

    sign = (n & (2 ** sgn_len - 1) * (2 ** (exp_len + mant_len))
            ) >> (exp_len + mant_len)
    exponent_raw = (n & ((2 ** exp_len - 1) * (2 ** mant_len))) >> mant_len
    mantissa = n & (2 ** mant_len - 1)

    sign_mult = 1
    if sign == 1:
        sign_mult = -1

    if exponent_raw == 2 ** exp_len - 1:  # Could be Inf or NaN
        if mantissa == 2 ** mant_len - 1:
            return float('nan')  # NaN

        return sign_mult * float('inf')  # Inf

    exponent = exponent_raw - (2 ** (exp_len - 1) - 1)

    if exponent_raw == 0:
        mant_mult = 0  # Gradual Underflow
    else:
        mant_mult = 1

    for b in range(mant_len - 1, -1, -1):
        if mantissa & (2 ** b):
            mant_mult += 1 / (2 ** (mant_len - b))

    return sign_mult * (2 ** exponent) * mant_mult


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def dateTimestamp():
    dateNow = datetime.now()
    dateNowTimestamp = dateNow.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    dateNowTimestamp = dateNowTimestamp+'+0800'
    return dateNowTimestamp


def dateToken():
    dateNow = datetime.now()
    dateNowToken = int(datetime.timestamp(dateNow.replace(microsecond=0)))
    dateNowTokenStr = str(dateNowToken)+'_'+str(dateNow.microsecond)
    return dateNowTokenStr


edm = EdmiReader('COM1', 9600)
# edm.TX_cmd(REG_SERIAL_NUMBER)
# print(list(edm.read2()))

# for v in buff_device_MV:
#     tempDevice = int(v['serialNumber']).to_bytes(4, byteorder='big')
#     broadCastVolt(tempDevice, 'SN')
#     edm.read2()


def singleVolt(phase):
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    if phase == 'R':
        function = REG_INSTAN_VOLTR
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'S':
        function = REG_INSTAN_VOLTS
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'T':
        function = REG_INSTAN_VOLTT
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[3:7]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = int(ieee_754_conversion(retValue))
    return retValue/1000


def broadCastVolt(source, phase):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    # edm.TX_byte(0x00)
    # crc = _update_crc(crc, 0x00)
    # # print(crc)
    # edm.TX_byte(0x00)
    # crc = _update_crc(crc, 0x00)
    # print(crc)

    if phase == 'R':
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x01)
        crc = _update_crc(crc, 0x01)

        function = REG_INSTAN_VOLTR
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'S':
        function = REG_INSTAN_VOLTS
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x02)
        crc = _update_crc(crc, 0x02)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'T':
        function = REG_INSTAN_VOLTT
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x03)
        crc = _update_crc(crc, 0x03)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = int(ieee_754_conversion(retValue))
    return retSerialNum, retValue/1000


def broadCastCurrent(source, phase):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    # edm.TX_byte(0x00)
    # crc = _update_crc(crc, 0x00)
    # # print(crc)
    # edm.TX_byte(0x00)
    # crc = _update_crc(crc, 0x00)
    # print(crc)

    if phase == 'R':
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x04)
        crc = _update_crc(crc, 0x04)

        function = REG_INSTAN_CURRR
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'S':
        function = REG_INSTAN_CURRS
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x05)
        crc = _update_crc(crc, 0x05)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'T':
        function = REG_INSTAN_CURRT
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x06)
        crc = _update_crc(crc, 0x06)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = int(ieee_754_conversion(retValue))
    return retSerialNum, retValue


def broadCastWatt(source, phase):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    if phase == 'R':
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x07)
        crc = _update_crc(crc, 0x07)

        function = REG_INSTAN_WATTR
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'S':
        function = REG_INSTAN_WATTS
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x08)
        crc = _update_crc(crc, 0x08)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if phase == 'T':
        function = REG_INSTAN_WATTT
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x09)
        crc = _update_crc(crc, 0x09)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = int(ieee_754_conversion(retValue))
    return retSerialNum, retValue


def broadCastPF(source):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    edm.TX_byte(0x00)
    crc = _update_crc(crc, 0x00)
    edm.TX_byte(0x10)
    crc = _update_crc(crc, 0x10)

    function = REG_INSTAN_PFACT
    for i in range(len(function)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(function[i])
        crc = _update_crc(crc, function[i])
        # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = ieee_754_conversion(retValue)
    return retSerialNum, round(retValue, 2)


def broadCastFreq(source):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    edm.TX_byte(0x00)
    crc = _update_crc(crc, 0x00)
    edm.TX_byte(0x11)
    crc = _update_crc(crc, 0x11)

    function = REG_INSTAN_FREQU
    for i in range(len(function)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(function[i])
        crc = _update_crc(crc, function[i])
        # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = ieee_754_conversion(retValue)
    return retSerialNum, round(retValue, 2)


def broadCastEnergy(source, types):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)
    # print(crc)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)
    # print(crc)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])
        # print(crc)

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])
        # print(crc)

    if types == 'kwhTotal':

        function = [0x52, 0x01, 0x69]
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x11)
        crc = _update_crc(crc, 0x11)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if types == 'kwhLWBP':  # LWBP

        function = [0x52, 0x01, 0x61]
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x12)
        crc = _update_crc(crc, 0x12)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if types == 'kwhBP':  # BP

        function = [0x52, 0x01, 0x60]
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x13)
        crc = _update_crc(crc, 0x13)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    if types == 'kvar':  # KVAR

        function = [0x52, 0x03, 0x69]  # KVARH
        edm.TX_byte(0x00)
        crc = _update_crc(crc, 0x00)
        edm.TX_byte(0x14)
        crc = _update_crc(crc, 0x14)
        for i in range(len(function)):
            # cmd_bytes = cmd[i].to_bytes(1, 'big')
            edm.TX_byte(function[i])
            crc = _update_crc(crc, function[i])
            # print(crc)

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = ieee_754_conversion(retValue)
    return retSerialNum, round(retValue, 2)


def broadCastTest(source, funct, index):
    broadCastAddress = [0xff, 0xff, 0xff, 0xff]
    edm.TX_raw(STX)
    stx = int.from_bytes(STX, byteorder='big')
    crc = _update_crc(0, stx)

    edm.TX_raw(D_E_FUNC.to_bytes(1, 'big'))
    crc = _update_crc(crc, D_E_FUNC)

    for i in range(len(source)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(source[i])
        crc = _update_crc(crc, source[i])

    for i in range(len(broadCastAddress)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(broadCastAddress[i])
        crc = _update_crc(crc, broadCastAddress[i])

    edm.TX_byte(0x00)
    crc = _update_crc(crc, 0x00)
    edm.TX_byte(index)
    crc = _update_crc(crc, index)

    function = funct
    for i in range(len(function)):
        # cmd_bytes = cmd[i].to_bytes(1, 'big')
        edm.TX_byte(function[i])
        crc = _update_crc(crc, function[i])

    edm.TX_byte(crc.to_bytes(2, 'big'))
    edm.TX_raw(ETX)

    tempRead = edm.read2()
    # print(tempRead)
    retSerialNum = tempRead[5:9]
    retValue = [int.from_bytes(x, byteorder='big', signed=False)
                for x in tempRead[14:18]]
    retValue = int.from_bytes(retValue, byteorder='big', signed=False)
    # newval = int.from_bytes(newval, ,
    # float_val = ieee_754_conversion(newval)
    retValue = ieee_754_conversion(retValue)
    print(retValue)
    return retSerialNum, retValue


def LVloop():
    for v in buff_device_LV:
        print("LOGIN")
        print(edm.login())
        # ret_login = parsingHeader()
        # if ret_login[0] == ACK and ret_login[1] == ACK:
        #     continues = True
        #     print("login accepted")
        # if not continues:
        #     print("login not accepted")
        #     continues = False
        source = int(v['serialNumber']).to_bytes(4, byteorder='big')
        print(v['type'])
        if v['type'] == 'MK10E':
            bodyValue = []
            for i in range(len(register_mk10)):

                serial, value = broadCastTest(source, register_mk10[i], i)
                # temDict = {
                #     "name": name_all_register[i],
                #     "val": value,
                #     "timestamp": dateTimestamp()
                # }
                # bodyValue.append(temDict)

        elif v['type'] == 'MK6N':
            for i in range(len(register_mk6n)):
                broadCastTest(source, register_mk6n[i], i)

        topic = 'huaweiss/0001/LVMeter/'+str(v['serialNumber'])
        print("Topic: %s" % topic)
        print("Message: %s" % str(bodyValue))
        dictMessage = {}
        dictMessage["token"] = dateToken()
        dictMessage["timestamp"] = dateTimestamp()
        dictMessage["body"] = bodyValue

        dictSend = {}
        dictSend['topic'] = topic
        dictSend['message'] = dictMessage

        dictSendStr = str(dictSend['message']).replace("'", '"')

        print(dictSend)
        client_mqtt = connect_mqtt()
        client_mqtt.publish(topic, dictSendStr)

        # print(dictSend)


def MVloop():
    for v in buff_device_MV:
        source = int(v['serialNumber']).to_bytes(4, byteorder='big')
        bodyValue = []
        if v['type'] == 'MK10E':
            for i in range(len(register_mk10)):
                broadCastTest(source, register_mk10[i], i)
        elif v['type'] == 'MK6N':
            for i in range(len(register_mk6n)):
                serial, value = broadCastTest(source, register_mk6n[i], i)
                temDict = {
                    "name": name_all_register[i],
                    "val": value,
                    "timestamp": dateTimestamp()
                }
                bodyValue.append(temDict)

        topic = 'huaweiss/0001/MVMeter/'+str(v['serialNumber'])
        print("Topic: %s" % topic)
        print("Message: %s" % str(bodyValue))
        dictMessage = {}
        dictMessage["token"] = dateToken()
        dictMessage["timestamp"] = dateTimestamp()
        dictMessage["body"] = bodyValue

        dictSend = {}
        dictSend['topic'] = topic
        dictSend['message'] = dictMessage

        dictSendStr = str(dictSend['message']).replace("'", '"')

        print(dictSend)
        client_mqtt = connect_mqtt()
        client_mqtt.publish(topic, dictSendStr)

# LVloop()
# MVloop()

# print(edm.login())
# ret_login = parsingHeader()
# if ret_login[0] == ACK and ret_login[1] == ACK:
#     continues = True
#     print("login accepted")
# if not continues:
#     print("login not accepted")
#     continues = False
# for i in range(len(register_mk6n)):
#     broadCastTest(source, register_mk6n[i], i)

# source = int(v['serialNumber']).to_bytes(4, byteorder='big')
# serial, voltR = broadCastVolt(
#     source, 'R')
# serial, voltS = broadCastVolt(
#     source, 'S')
# serial, voltT = broadCastVolt(
#     source, 'T')

# serial, currR = broadCastCurrent(
#     source, 'R')
# serial, currS = broadCastCurrent(
#     source, 'S')
# serial, currT = broadCastCurrent(
#     source, 'T')

# serial, wattR = broadCastWatt(
#     source, 'R')
# serial, wattS = broadCastWatt(
#     source, 'S')
# serial, wattT = broadCastWatt(
#     source, 'T')

# serial, pf = broadCastPF(
#     source)
# serial, freq = broadCastFreq(
#     source)

# serial, kvar = broadCastEnergy(source, 'kvar')
# serial, kwhBP = broadCastEnergy(source, 'kwhBP')
# serial, kwhLWBP = broadCastEnergy(source, 'kwhLWBP')
# serial, kwhTotal = broadCastEnergy(source, 'kwhTotal')

# serial = [int.from_bytes(x, byteorder='big', signed=False)
#           for x in serial]
# serial = int.from_bytes(serial, byteorder='big', signed=False)
# print(serial)

# print(voltR)
# print(voltS)
# print(voltT)
# print(currR)
# print(currS)
# print(currT)
# print(wattR)
# print(wattS)
# print(wattT)
# print(pf)
# print(freq)
# print(kvar)
# print(kwhBP)
# print(kwhLWBP)
# print(kwhTotal)


# print("Topic: %s" % topic)
# print("Message: %s" % str(bodyValue))
# dictMessage = {}
# dictMessage["token"] = dateToken()
# dictMessage["timestamp"] = dateTimestamp()
# dictMessage["body"] = bodyValue

# dictSend = {}
# dictSend['topic'] = topic
# dictSend['message'] = dictMessage

# dictSendStr = str(dictSend['message']).replace("'", '"')
Topic = 'huawei/0001/LVMeter/218169134'
body = [{'name': 'voltR', 'val': 48.1038532608, 'timestamp': '2024-02-28T07:22:47.899+0800'}, {'name': 'voltS', 'val': 231.2630157470703, 'timestamp': '2024-02-28T07:22:47.978+0800'}, {'name': 'voltT', 'val': 231.25100708007812, 'timestamp': '2024-02-28T07:22:48.043+0800'}, {'name': 'currR', 'val': 0.020800000056624413, 'timestamp': '2024-02-28T07:22:48.108+0800'}, {'name': 'currS', 'val': 0.0, 'timestamp': '2024-02-28T07:22:48.187+0800'}, {'name': 'currT', 'val': 0.0, 'timestamp': '2024-02-28T07:22:48.235+0800'}, {'name': 'wattR', 'val': 2.1000001430511475, 'timestamp': '2024-02-28T07:22:48.283+0800'}, {'name': 'wattS',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    'val': 0.0, 'timestamp': '2024-02-28T07:22:48.332+0800'}, {'name': 'wattT', 'val': 0.0, 'timestamp': '2024-02-28T07:22:48.398+0800'}, {'name': 'pf', 'val': 0.4620000123977661, 'timestamp': '2024-02-28T07:22:48.475+0800'}, {'name': 'freq', 'val': 50.052001953125, 'timestamp': '2024-02-28T07:22:48.539+0800'}, {'name': 'kvarh', 'val': 0.0, 'timestamp': '2024-02-28T07:22:48.588+0800'}, {'name': 'kwhBP', 'val': 18.0, 'timestamp': '2024-02-28T07:22:48.683+0800'}, {'name': 'kwhLBP', 'val': 0.0, 'timestamp': '2024-02-28T07:22:48.732+0800'}, {'name': 'kwhtotal', 'val': 18.0, 'timestamp': '2024-02-28T07:22:48.796+0800'}]
dictMessage = {}
dictMessage["token"] = dateToken()
dictMessage["timestamp"] = dateTimestamp()
dictMessage["body"] = body

dictMessage = str(dictMessage)

dictSendStr = str(dictMessage.replace("'", '"'))

client_mqtt = connect_mqtt()
client_mqtt.publish(Topic, dictSendStr)
