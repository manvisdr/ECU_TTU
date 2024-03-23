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
client_id = f'asda'
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
    client.clientAddress = int(v['clientAddress'])
    if client.serverAddress != 1:
        client.serverAddress = GXDLMSClient.getServerAddress(
            client.serverAddress, int(v['serverAddress']))
    else:
        client.serverAddress = int(v['serverAddress'])

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
    print(client.getInterfaceType())

    if dicts['auth'] == "None".lower():
        client.authentication = Authentication.NONE
    elif dicts['auth'] == "Low".lower():
        client.authentication = Authentication.LOW
    elif dicts['auth'] == "High".lower():
        client.authentication = Authentication.HIGH
    elif dicts['auth'] == "HighMd5".lower():
        client.authentication = Authentication.HIGH_MD5
    elif dicts['auth'] == "HighSha1".lower():
        client.authentication = Authentication.HIGH_SHA1
    elif dicts['auth'] == "HighGMac".lower():
        client.authentication = Authentication.HIGH_GMAC
    elif dicts['auth'] == "HighSha256".lower():
        client.authentication = Authentication.HIGH_SHA256

    if dicts['password'] != '':
        client.password = dicts['password']

    if 'securityLevel' in dicts:
        if dicts['securityLevel'] == "None".lower():
            client.ciphering.security = Security.NONE
        elif dicts['securityLevel'] == "Authentication".lower():
            client.ciphering.security = Security.AUTHENTICATION
        elif dicts['securityLevel'] == "Encryption".lower():
            client.ciphering.security = Security.ENCRYPTION
        elif dicts['securityLevel'] == "AuthenticationEncryption".lower():
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

clients = connect_mqtt()


def readProfile(reader, count=24):
    rows = []
    try:
        loadProfile = reader.client.settings.objects.findByLN(
            ObjectType.PROFILE_GENERIC, '1.0.99.1.0.255')
        captureObjects = reader.read(loadProfile, 3)
        capturePeriod = reader.read(loadProfile, 4)
        sortMethod = reader.read(loadProfile, 5)
        sortObject = reader.read(loadProfile, 6)
        entriesInUse = reader.read(loadProfile, 7)
        entries = reader.read(loadProfile, 8)
        BeginOfreadedEntries = entriesInUse - count - 1
        rows = reader.readRowsByEntry(loadProfile, BeginOfreadedEntries, count)

    except Exception as e:
        print(e)
    return rows


def readProfileDate(reader, count=24):
    rows = []

    loadProfile = reader.client.settings.objects.findByLN(
        ObjectType.PROFILE_GENERIC, '1.0.99.1.0.255')
    captureObjects = reader.read(loadProfile, 3)

    val = reader.readRowsByEntry(loadProfile, 1, 1)
    print(val)
    # rows = reader.readRowsByRange(loadProfile, BeginOfreadedEntries, count)

    return rows


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
        # disconControl = GXDLMSDisconnectControl('0.0.96.3.10.255')

        loadProfile = GXDLMSProfileGeneric("1.0.99.1.0.255")
        captureObjects = reader.read(loadProfile, 3)
        capturePeriod = reader.read(loadProfile, 4)
        sortMethod = reader.read(loadProfile, 5)
        sortObject = reader.read(loadProfile, 6)
        entriesInUse = reader.read(loadProfile, 7)
        entries = reader.read(loadProfile, 8)
        start_time = datetime(2023, 9, 1, 20, 50, 0)
        end_time = datetime(2023, 9, 1, 20, 40, 0)
        # aa = reader.readRowsByRange(loadProfile, start_time, end_time)

        aa = reader.readRowsByEntry(loadProfile, 1, 200)
        for item in aa:
            timestamp = item[0]
            volt = item[2]
            kwh = item[10]

            print(
                f"Timestamp: {timestamp} | volt: {volt/10} V | KWH: {kwh} kWh")

        # reader.readDataBlock(disconControl.remoteDisconnect(client), reply)
        # reader.readDataBlock(disconControl.remoteReconnect(client), reply)

        # for val in obis:

        #     if val['type'] == 'data':
        #         obis = val['obis']
        #         obj = GXDLMSData(obis)
        #         readed = reader.read(obj, 2)
        #         if (type(readed) == str):
        #             readed = readed.decode("utf-8")
        #         print(readed)
        #         temDict = {
        #             "name": val['name'],
        #             "val": readed,
        #             "timestamp": dateTimestamp()
        #         }
        #         bodyValue.append(temDict)

        #     elif val['type'] == 'register':
        #         obis = val['obis']
        #         obj = GXDLMSRegister(obis)
        #         read_unit = reader.read(obj, 3)
        #         read_value = reader.read(obj, 2)
        #         temDict = {
        #             "name": val['name'],
        #             "val": read_value,
        #             "timestamp": dateTimestamp()
        #         }
        #         bodyValue.append(temDict)
        #         # print(read_value)

        # reader.close()
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


# def getInstant():


# for i in readyData:
#     print(i['topic'])
#     print(i['message'])
#     result = clients.publish(i['topic'], str(i['message']).replace("'", '"'))
