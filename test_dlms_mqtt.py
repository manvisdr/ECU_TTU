from gurux_dlms.enums import InterfaceType, Authentication, Security, Standard
from gurux_dlms import GXDLMSClient
from gurux_dlms.secure import GXDLMSSecureClient
from gurux_dlms.GXByteBuffer import GXByteBuffer
from gurux_dlms.objects import GXDLMSObject
from gurux_dlms.objects.enums import ControlMode, ControlState
from gurux_common.enums import TraceLevel
from gurux_common.io import Parity, StopBits, BaudRate
from gurux_net.enums import NetworkType
from gurux_net import GXNet
from gurux_serial.GXSerial import GXSerial

from gurux_dlms.GXDateTime import GXDateTime
from gurux_dlms.internal._GXCommon import _GXCommon
from gurux_dlms import GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError, GXDLMSTranslator
from gurux_dlms import GXByteBuffer, GXDLMSTranslatorMessage, GXReplyData
from gurux_dlms.enums import RequestTypes, Security, InterfaceType, ObjectType, DataType
from gurux_dlms.secure.GXDLMSSecureClient import GXDLMSSecureClient
from gurux_dlms.objects import GXDLMSObject, GXDLMSObjectCollection, GXDLMSData, GXDLMSRegister,\
    GXDLMSDemandRegister, GXDLMSProfileGeneric, GXDLMSExtendedRegister, GXDLMSDisconnectControl
from GXDLMSReader import GXDLMSReader

from datetime import datetime
import json


from paho.mqtt import client as mqtt_client
broker = '203.194.112.238'
port = 1883
client_id = f'asdasdfsfds'
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


jsonFileName = 'dlms_conf_copy.json'
jsonFile = open(jsonFileName, 'r')
jsonFileLoad = json.loads(jsonFile.read())
dlmsConf = []

readyData = []


def mediaSettings(dicts=dict):
    media = GXSerial(None)
    media.port = dicts['com']
    media.baudRate = int(dicts['baudRate'])
    media.dataBits = 8
    media.parity = Parity.NONE
    media.stopbits = StopBits.ONE
    return media


def clientSettings(dicts=dict):
    client = GXDLMSSecureClient(True)
    client.clientAddress = int(dicts['clientAddress'])

    if client.serverAddress != 1:
        client.serverAddress = GXDLMSClient.getServerAddress(
            client.serverAddress, int(dicts['serverAddress']))
    else:
        client.serverAddress = int(dicts['serverAddress'])

    if dicts['interface'].lower() == "HDLC".lower():
        print("INTERFACE : HDLC")
        client.interfaceType = InterfaceType.HDLC
    elif dicts['interface'].lower() == "WRAPPER".lower():
        print("INTERFACE : WRAPPER")
        client.interfaceType = InterfaceType.WRAPPER
    elif dicts['interface'].lower() == "HdlcWithModeE".lower():
        print("INTERFACE : HDLC_WITH_MODE_E")
        client.interfaceType = InterfaceType.HDLC_WITH_MODE_E
    elif dicts['interface'].lower() == "Plc".lower():
        print("INTERFACE : PLC")
        client.interfaceType = InterfaceType.PLC
    elif dicts['interface'].lower() == "PlcHdlc".lower():
        print("INTERFACE : PLC_HDLC")
        client.interfaceType = InterfaceType.PLC_HDLC

    if dicts['auth'].lower() == "None".lower():
        client.authentication = Authentication.NONE
        print("AUTH NONE")
    elif dicts['auth'].lower() == "Low".lower():
        client.authentication = Authentication.LOW
        print("AUTH LOW")
    elif dicts['auth'].lower() == "High".lower():
        client.authentication = Authentication.HIGH
    elif dicts['auth'].lower() == "HighMd5".lower():
        client.authentication = Authentication.HIGH_MD5
    elif dicts['auth'].lower() == "HighSha1".lower():
        client.authentication = Authentication.HIGH_SHA1
    elif dicts['auth'].lower() == "HighGMac".lower():
        client.authentication = Authentication.HIGH_GMAC
    elif dicts['auth'].lower() == "HighSha256".lower():
        client.authentication = Authentication.HIGH_SHA256

    if dicts['password'] != '':
        client.password = dicts['password']

    if 'securityLevel' in dicts:
        if dicts['securityLevel'].lower() == "None".lower():
            client.ciphering.security = Security.NONE
        elif dicts['securityLevel'].lower() == "Authentication".lower():
            client.ciphering.security = Security.AUTHENTICATION
        elif dicts['securityLevel'].lower() == "Encryption".lower():
            client.ciphering.security = Security.ENCRYPTION
        elif dicts['securityLevel'].lower() == "AuthenticationEncryption".lower():
            client.ciphering.security = Security.AUTHENTICATION_ENCRYPTION

    if 'systemTitle' in dicts:
        client.ciphering.systemTitle = GXByteBuffer.hexToBytes(
            dicts['securityLevel'])
    if 'authKey' in dicts:
        client.ciphering.authenticationKey = GXByteBuffer.hexToBytes(
            dicts['authKey'])
    if 'blockKey' in dicts:
        client.ciphering.blockCipherKey = GXByteBuffer.hexToBytes(
            dicts['blockKey'])

    return client


for v in jsonFileLoad:
    dlmsConf.append(v)


for i in dlmsConf:
    for v in i['body']:

        trace = TraceLevel.VERBOSE
        invocationCounter = None
        obis = v['obis']

        media = mediaSettings(v)
        client = clientSettings(v)

        reader = GXDLMSReader(client, media, trace, invocationCounter)
        media.open()

        reader.initializeConnection()

        bodyValue = []
        reply = GXReplyData()

        for val in obis:
            if val['type'] == 'data':
                obis = val['obis']
                obj = GXDLMSData(obis)
                readed = reader.read(obj, 2)
                if type(readed) == str:
                    readed = readed
                else:
                    readed = readed.decode("utf-8")
                temDict = {
                    "name": val['name'],
                    "val": readed,
                    "timestamp": dateTimestamp()
                }
                bodyValue.append(temDict)

            elif val['type'] == 'register':
                obis = val['obis']
                obj = GXDLMSRegister(obis)
                read_unit = reader.read(obj, 3)
                read_value = reader.read(obj, 2)
                temDict = {
                    "name": val['name'],
                    "val": read_value,
                    "timestamp": dateTimestamp()
                }
                print(temDict)
                bodyValue.append(temDict)
                # print(read_value)

        reader.close()
        # topic = 'huaweiss/'+i['app']+'/'+bodyValue[0]['val']
        # print("Topic: %s" % topic)
        # print("Message: %s" % str(bodyValue))
        # dictMessage = {}
        # dictMessage["token"] = dateToken()
        # dictMessage["timestamp"] = dateTimestamp()
        # dictMessage["body"] = bodyValue

        # dictSend = {}
        # dictSend['topic'] = topic
        # dictSend['message'] = dictMessage

        # readyData.append(dictSend)


# for i in readyData:
#     print(i['topic'])
#     print(i['message'])
#     result = clients.publish(i['topic'], str(i['message']).replace("'", '"'))


# def run():
#     client_mqtt = connect_mqtt()
#     # subscribe(client_mqtt)
#     client_mqtt.loop_forever()


# if __name__ == '__main__':
#     run()
