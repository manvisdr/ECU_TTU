import serial
import struct
from datetime import datetime
import json

from paho.mqtt import client as mqtt_client
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

REG_INSTAN_VOLTR = [0xE0, 0x00]  # VOLTAGE PHASE A
REG_INSTAN_VOLTS = [0xE0, 0x01]  # VOLTAGE PHASE B
REG_INSTAN_VOLTT = [0xE0, 0x02]  # VOLTAGE PHASE C
REG_INSTAN_CURRR = [0xE0, 0x10]  # CURRENT PHASE A
REG_INSTAN_CURRS = [0xE0, 0x11]  # CURRENT PHASE B
REG_INSTAN_CURRT = [0xE0, 0x12]  # CURRENT PHASE C
REG_INSTAN_WATTR = [0xE0, 0x30]  # WATT PHASE A
REG_INSTAN_WATTS = [0xE0, 0x31]  # WATT PHASE B
REG_INSTAN_WATTT = [0xE0, 0x32]  # WATT PHASE C
REG_INSTAN_PFACT = [0xE0, 0x26]  # POWER FACTOR
REG_INSTAN_FREQU = [0xE0, 0x60]  # FREQUENCY
REG_ENERGY_KVARH = [0x1E, 0x20]  # TOU ENERGY KVARH
REG_ENERGY_KWHLBP = [0x1E, 0x01]  # TOU ENERGY
REG_ENERGY_KWHBP = [0x1E, 0x02]
REG_ENERGY_KWHTOT = [0x1E, 0x00]


class EdmiReader:
    def __init__(self, port, baud):
        self.serial = serial.Serial(port)
        self.serial.baudrate = baud

    def TX_raw(self, ch):
        self.serial.write(ch)
        # self.serial.flush()

    def TX_byte(self, d):
        # if d == STX:
        # if d == ETX:
        # if d == DLE:
        # if d == XON:
        if d == XOFF:
            self.TX_raw(DLE)
            self.TX_raw(d | 0x40)
        else:
            self.TX_raw(d)


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


ser = serial.Serial('COM10', 9600, timeout=1)


login = [0x02, 0x4C, 0x45, 0x44, 0x4D, 0x49, 0x2C, 0x49, 0x4D,
         0x44, 0x45, 0x49, 0x4D, 0x44, 0x45, 0x00, 0xD9, 0x69, 0x03]
voltR = [0x02, 0x52, 0xE0, 0x00, 0xCD, 0x74, 0x03]
voltS = [0x02, 0x52, 0xE0, 0x01, 0xDD, 0x55, 0x03]
voltT = [0x02, 0x52, 0xE0, 0x10, 0x42, 0xED, 0x36, 0x03]
currR = [0x02, 0x52, 0xE0, 0x10, 0x50, 0xDF, 0x45, 0x03]
currS = [0x02, 0x52, 0xE0, 0x10, 0x50, 0xDF, 0x45, 0x03]
currT = [0x02, 0x52, 0xE0, 0x12, 0xFF, 0x07, 0x03]
wattR = [0x02, 0x52, 0xE0, 0x30, 0xFB, 0x27, 0x03]
wattS = [0x02, 0x52, 0xE0, 0x31, 0xEB, 0x06, 0x03]
wattT = [0x02, 0x52, 0xE0, 0x32, 0xDB, 0x65, 0x03]
pf = [0x02, 0x52, 0xE0, 0x26, 0x89, 0xD0, 0x03]
freq = [0x02, 0x52, 0xE0, 0x60, 0xA1, 0xD2, 0x03]
kvarh = [0x02, 0x52, 0x1E, 0x10, 0x50, 0xEF, 0x8B, 0x03]
kwhLBP = [0x02, 0x52, 0x1E, 0x01, 0xED, 0x9B, 0x03]
kwhBP = [0x02, 0x52, 0x1E, 0x10, 0x42, 0xDD, 0xF8, 0x03]
kwhtotal = [0x02, 0x52, 0x1E, 0x00, 0xFD, 0xBA, 0x03]
serialnumber = [0x02, 0x52, 0xF0, 0x10, 0x42, 0xEE, 0x45, 0x03]

all_register = [voltR, voltS, voltT, currR, currS, currT,
                wattR, wattS, wattT, pf, freq, kvarh, kwhLBP, kwhBP, kwhtotal]
name_all_register = ["voltR", "voltS", "voltT", "currR", "currS", "currT",
                     "wattR", "wattS", "wattT", "pf", "freq", 'kvarh', "kwhLBP", "kwhBP", "kwhtotal"]


def bitwise_and_bytes(a, b):
    result_int = int.from_bytes(
        a, byteorder="big") & int.from_bytes(b, byteorder="big")
    return result_int.to_bytes(max(len(a), len(b)), byteorder="big")


def parsingHeader():
    counter = 0
    dlechar = False
    message = []
    index = 0
    completeMsg = False
    while True:
        inChar = ser.read()
        if completeMsg:
            break
        if inChar == b'\x02':
            while True:
                inChar = ser.read()
                # print(inChar)
                if inChar != b'\x03':
                    if (inChar == b'\x10'):
                        dlechar = True
                    else:
                        if (dlechar):
                            inChar = bitwise_and_bytes(inChar, b'\xBF')
                        dlechar = False
                        message.append(inChar)
                        index += 1
                else:
                    completeMsg = True
                    break
    return message


continues = False
ser.write(bytearray(login))
ret_login = parsingHeader()
if ret_login[0] == ACK and ret_login[1] == ACK:
    continues = True
    print("login accepted")
if not continues:
    print("login not accepted")
    continues = False

bodyValue = []

strSN = ''
ser.write(bytearray(serialnumber))
ret_serialNumber = parsingHeader()
if ret_serialNumber[0] == R_FUNC:
    for v in range(len(ret_serialNumber)-6):
        strSN += ret_serialNumber[v + 3].decode("utf-8")
topic = 'huawei/0001/LVMeter/'+strSN
temDict = {
    "name": 'sn',
    "val": strSN,
    "timestamp": dateTimestamp()
}
bodyValue.append(temDict)


for i in range(len(all_register)):
    if continues:
        ser.write(bytearray(all_register[i]))
        ret_buffer = parsingHeader()
        if ret_buffer[0] == R_FUNC:
            outbuffer = ret_buffer[3:7]
            print(outbuffer)
            # struct.unpack("f",
            tempData = struct.unpack('>f', b''.join(outbuffer))
            tempData = float(tempData[0])
            if name_all_register[i] == 'voltR' or name_all_register[i] == 'voltS' or name_all_register[i] == 'voltT':
                tempData = tempData/1000
            elif name_all_register[i] == 'wattR' or name_all_register[i] == 'wattS' or name_all_register[i] == 'wattT':
                tempData = tempData/10
            elif name_all_register[i] == 'kvarh' or name_all_register[i] == "kwhBP" or name_all_register[i] == 'kwhLBP' or name_all_register[i] == 'kwhtotal':
                tempData = tempData/1000
            temDict = {
                "name": name_all_register[i],
                "val": tempData,
                "timestamp": dateTimestamp()
            }
            bodyValue.append(temDict)
            # print(temDict)
            continues = True
        else:
            print("not get data")
            continues = False


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

client_mqtt = connect_mqtt()
client_mqtt.publish(topic, dictSendStr)
