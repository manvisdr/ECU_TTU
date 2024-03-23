import json
import serial
import time
from datetime import datetime
import os
import re

from paho.mqtt import client as mqtt_client
import paho.mqtt.publish as publish

broker = '203.194.112.238'
port = 1883
client_id = f'wasionmeter'
username = 'das'
password = 'mgi2022'


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


request_first = b'\x00\x01\x00\x10\x00\x01\x00\x1f\x60\x1d\xa1\x09\x06\x07\x60\x85\x74\x05\x08\x01\x01\xbe\x10\x04\x0e\x01\x00\x00\x00\x06\x5f\x1f\x04\x00\x00\x7e\x1f\xff\xff'


request_current = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x1F\x07\x00\xFF\x03\x00'
request_voltage = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x03\x00'
request_power_factor = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x21\x07\x00\xFF\x03\x00'
request_watt = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x15\x07\x00\xFF\x03\x00'
request_var = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x07\x00\xFF\x03\x00'
request_pos_kwh = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x01\x08\x00\xFF\x03\x00'
request_neg_kwh = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x02\x08\x00\xFF\x03\x00'
request_pos_kvarh = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x08\x00\xFF\x03\x00'
request_neg_kvarh = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x04\x08\x00\xFF\x03\x00'

request_block = [request_first, request_current, request_voltage, request_power_factor,
                 request_watt, request_var, request_pos_kwh, request_neg_kwh, request_pos_kvarh, request_neg_kvarh]


def read2(seri, start_time):
    counter = 0
    dlechar = False
    msg_byte = b''
    message = []
    index = 0
    completeMsg = False

    while True:
        # if (self.serial.inWaiting() > 0):
        if (time.time() - start_time) > 5:
            break
        inChar = b''
        if inChar == b'\x68':
            while True:
                inChar = seri.read()
                print(inChar)
                if inChar != b'\x16':
                    message.append(inChar)
                    msg_byte += msg_byte+inChar
                    index += 1
                else:
                    print("completeMsg")
                    completeMsg = True
                    break

    # else:
        if completeMsg:
            break
    return message


def make13762(destination, dlmsData):
    header = b'\x68'  # Frame header

    control_word = b'\x41'
    information_field = b'\x04\x00\xff\x00\x00'  # Information field
    frame_serial_number = b'\x83'  # 3762 frame serial number
    # source_address = b'\x01\x00\x01\x30\x02\x29'  # Source address
    source_address = b'\x36\x01\x00\x00\x00\x00'
    # Destination address: indicates the address of the table to be read
    destination_addres = destination  # meter 1
    # destination_addres = b'\x38\x00\x00\x19\x46\x02'  # meter 2
    function = b'\x13\x02\x00'  # AFN=13, Fn=2, means：Meter readig
    # Communication protocol type: transparent transmission
    transparent_protocol = b'\x00'
    packet_content = dlmsData
    packet_length = len(packet_content).to_bytes(1, 'big') + \
        b'\x00'  # The packet length is 2 bytes [2700]
    # print(len(packet_content))
    frame_end = b'\x16'  # Frame end
    all_length = 30 + len(packet_content)
    frame_length = all_length.to_bytes(1, 'big') + b'\x00'

    a = control_word+information_field+frame_serial_number + source_address+destination_addres+function + \
        transparent_protocol+packet_length+packet_content
    aa = 0
    for i in range(len(a)):
        # print(a[i])
        aa += int(a[i])
        # print(aa)

    crc = aa & 0xFF
    crc_bytes = crc.to_bytes(1, 'big')
    command = header+frame_length+control_word+information_field+frame_serial_number + source_address + \
        destination_addres+function + transparent_protocol + \
        packet_length+packet_content+crc_bytes+frame_end
    return command


def onephase_current(destination, ser=serial):
    request_current_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x1F\x07\x00\xFF\x03\x00'
    request_current_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x1F\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_current_3))
    time.sleep(1)
    msg = b''
    ser.write(make13762(destination, request_current_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Current")
    # print(val)
    print(value/1000)
    return value/1000


def onephase_volt(destination, ser=serial):
    request_current_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x03\x00'
    request_current_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_current_3))
    time.sleep(1)
    ser.write(make13762(destination, request_current_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Volt")
    # print(val)
    print(value/10)
    return value/10


def onephase_freq(destination, ser=serial):
    request_freq_3 = b'\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x0E\x07\x00\xFF\x03\x00'
    request_freq_2 = b'\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x0E\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_freq_3))
    time.sleep(1)
    ser.write(make13762(destination, request_freq_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-4:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Freq")
    # print(val)
    print(value/100)
    return value/100


def onephase_power_factor(destination, ser=serial):
    request_power_factor_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x21\x07\x00\xFF\x03\x00'
    request_power_factor_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x21\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_power_factor_3))
    time.sleep(1)
    ser.write(make13762(destination, request_power_factor_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Power Factor")
    # print(val)
    print(value/1000)
    return value/1000


def onephase_watt(destination, ser=serial):
    request_watt_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x15\x07\x00\xFF\x03\x00'
    request_watt_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x15\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_watt_3))
    time.sleep(1)
    ser.write(make13762(destination, request_watt_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Watt")
    # print(val)
    print(value)
    return value


def onephase_var(destination, ser=serial):
    request_var_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x07\x00\xFF\x03\x00'
    request_var_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x07\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_var_3))
    time.sleep(1)
    ser.write(make13762(destination, request_var_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("Var")
    # print(val)
    print(value)
    return value


def onephase_pos_kwh(destination, ser=serial):
    request_pos_kwh_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x01\x08\x00\xFF\x03\x00'
    request_pos_kwh_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x01\x08\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_pos_kwh_3))
    time.sleep(1)
    ser.write(make13762(destination, request_pos_kwh_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("POS KWH")
    # print(val)
    print(value)
    return value


def onephase_neg_kwh(destination, ser=serial):
    request_neg_kwh_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x08\x00\xFF\x03\x00'
    request_neg_kwh_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x08\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_neg_kwh_3))
    time.sleep(1)
    ser.write(make13762(destination, request_neg_kwh_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("neg kwh")
    # print(val)
    print(value)
    return value


def onephase_pos_kvarh(destination, ser=serial):
    request_pos_kvarh_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x08\x00\xFF\x03\x00'
    request_pos_kvarh_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x03\x08\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_pos_kvarh_3))
    time.sleep(1)
    ser.write(make13762(destination, request_pos_kvarh_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("pos kvar")
    # print(val)
    print(value)
    return value


def onephase_neg_kvarh(destination, ser=serial):
    request_neg_kvarh_3 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x04\x08\x00\xFF\x03\x00'
    request_neg_kvarh_2 = b'\00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x04\x08\x00\xFF\x02\x00'
    ser.write(make13762(destination, request_neg_kvarh_3))
    time.sleep(1)
    ser.write(make13762(destination, request_neg_kvarh_2))
    msg = b''
    while (True):
        try:
            a = ser.read()
            msg += a
            # print(a.hex(), end=" ")
            if a == b'\x16':
                break
        except serial.serialutil.SerialException:
            b = ''
    val = msg[-6:len(a)-3]
    value = int.from_bytes(val, byteorder='big', signed=False)
    print("neg kvar")
    # print(val)
    print(value)
    return value


# '/root/kwh_list.json'
jsonFileName = '/root/kwh_list.json'
jsonFile = open(jsonFileName, 'r')
jsonFileLoad = json.loads(jsonFile.read())

meterConf = []
for v in jsonFileLoad:
    meterConf.append(v)

listMeter1Phasa_asli = []
listMeter3Phasa_asli = []
listMeter1Phasa = []
listMeter3Phasa = []
for i in meterConf:
    for v in i['serialNumber']:
        if i['type'] == 1:
            listMeter1Phasa_asli.append(v)
            listMeter1Phasa.append(bytes.fromhex(v)[::-1])
        if i['type'] == 3:
            listMeter3Phasa_asli.append(v)
            listMeter3Phasa.append(bytes.fromhex(v)[::-1])

print(listMeter1Phasa_asli)
print(listMeter3Phasa_asli)
print(listMeter1Phasa)
print(listMeter3Phasa)

ser = serial.Serial('/dev/ttyRS4', 115200, timeout=2)

# clients = connect_mqtt()
for i in range(len(listMeter1Phasa)):
    bodyValue = []
    destination = listMeter1Phasa[i]
    ser.write(make13762(destination, request_first))
    time.sleep(1)

    value = onephase_current(destination, ser)
    temDict = {
        "name": "current",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_volt(destination, ser)
    temDict = {
        "name": "Volt",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_power_factor(destination, ser)
    temDict = {
        "name": "pF",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_watt(destination, ser)
    temDict = {
        "name": "watt",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_freq(destination, ser)
    temDict = {
        "name": "freq",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_var(destination, ser)
    temDict = {
        "name": "var",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_pos_kwh(destination, ser)
    temDict = {
        "name": "pos_kwh",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_neg_kwh(destination, ser)
    temDict = {
        "name": "neg_kwh",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_pos_kvarh(destination, ser)
    temDict = {
        "name": "pos_varh",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    value = onephase_neg_kvarh(destination, ser)
    temDict = {
        "name": "neg_varh",
        "val": value,
        "timestamp": dateTimestamp()
    }
    bodyValue.append(temDict)

    dictMessage = {}
    dictMessage["token"] = dateToken()
    dictMessage["timestamp"] = dateTimestamp()
    dictMessage["body"] = bodyValue

    dictSend = {}
    dictSend['topic'] = 'DLMS/'+listMeter1Phasa_asli[i]
    dictSend['message'] = dictMessage

    # result = clients.publish(dictSend['topic'], str(dictSend['message']).replace("'", '"'))
    # mqttc = mqtt_client.Client("python_pub")
    # mqttc.connect(broker, 1883)
    # mqttc.publish("test/test", "Hello world!")
    # msg = str(dictSend['message']).replace('"', re.escape('\"'))
    # print(msg)
    # os.system('mosquitto_pub -m '+msg+' -t '+dictSend['topic'])
    publish.single(dictSend['topic'], str(
        dictSend['message']).replace("'", '"'), hostname="localhost")