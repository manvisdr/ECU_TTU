import time
import json
from datetime import datetime
from paho.mqtt import client as mqtt_client

broker = '190.92.220.180'
port = 1883
client_id = f'lineloss_laptop'
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


dlmsId = []
dlmsKWH = []
dlmsKWHLast = []
dlmsKWH_adding = 0

LVId = []
LVKWH = []
LVKWHLast = []
LVKSH_adding = 0

dataadding = 0


def subscribe(clientmqtt: mqtt_client):
    global countClientDlms

    def on_message(client, userdata, msg):
        # print(msg.topic)
        global dlmsKWH_adding
        global LVKWHLast

        # if 'DLMS' in msg.topic:
        #     tempDLMS = json.loads(msg.payload)
        #     if tempDLMS['body'][0]['val'] not in dlmsId:
        #         dlmsId.append(tempDLMS['body'][0]['val'])
        #         print('adding new dlms id')
        #         for v in tempDLMS['body']:
        #             if v['name'] == 'pos_kwh':
        #                 dlmsKWH.append(
        #                     [tempDLMS['body'][0]['val'], int(v['val'])])
        #                 dlmsKWHLast.append(
        #                     [tempDLMS['body'][0]['val'], int(v['val'])])
        #     else:
        #         for v in tempDLMS['body']:
        #             for i in range(len(dlmsKWH)):
        #                 if dlmsKWH[i][0] == tempDLMS['body'][0]['val'] and v['name'] == 'pos_kwh':
        #                     # if tempDLMS['body'][0]['val'] == dlmsKWH and v['name'] == 'pos_kwh':
        #                     dlmsKWHLast[i][1] = dlmsKWH[i][1]
        #                     dlmsKWH[i][1] = int(v['val'])

        #     for i in range(len(dlmsKWH)):
        #         a = dlmsKWH[i][1] - dlmsKWHLast[i][1]
        #         dlmsKWH_adding += a
        #         # print(dlmsKWH_adding)

        # if 'LVMeter' in msg.topic:
        #     tempLV = json.loads(msg.payload)
        #     if tempLV['body'][0]['val'] not in LVId:
        #         LVId.append(tempLV['body'][0]['val'])
        #         print('adding new lvmeter id')
        #         for v in tempLV['body']:
        #             if v['name'] == 'kwhtotal':
        #                 LVKWH.append(
        #                     [tempLV['body'][0]['val'], int(v['val'])/10])
        #                 LVKWHLast.append(
        #                     [tempLV['body'][0]['val'], int(v['val'])/10])
        #                 # print(LVKWH)
        #     else:
        #         for v in tempLV['body']:
        #             for i in range(len(LVKWH)):
        #                 if LVKWH[i][0] == tempLV['body'][0]['val'] and v['name'] == 'kwhtotal':
        #                     # if tempLV['body'][0]['val'] == dlmsKWH and v['name'] == 'pos_kwh':
        #                     # print(LVKWH)
        #                     LVKWHLast[i][1] = LVKWH[i][1]
        #                     LVKWH[i][1] = int(v['val'])/10

        #     for i in range(len(LVKWH)):
        #         a = LVKWH[i][1] - LVKWHLast[i][1]
        #         LVEnergy = a

        #         # print(dlmsKWH_adding)
        #         print("AMI KWH TOTAL PER MENIT")
        #         print(dlmsKWH_adding)
        #         print("LVMETER TOTAL PER MENIT")
        #         print(a)
        #         print("LINELOSS")
        #         bodyValue = []
        #         if a == 0:
        #             print("AWAL")
        #             loss_val = {
        #                 "name": "lossVal",
        #                 "val": abs(LVEnergy-dlmsKWH_adding),
        #                 "timestamp": dateTimestamp()
        #             }
        #             lvEnergyAll = {
        #                 "name": "branchEnergy",
        #                 "val": LVEnergy,
        #                 "timestamp": dateTimestamp()
        #             }
        #             meterEnergy = {
        #                 "name": "meterEnergy",
        #                 "val": dlmsKWH_adding,
        #                 "timestamp": dateTimestamp()
        #             }
        #             # lineLossFormula = ((abs(a-dlmsKWH_adding))/a)*100
        #             linelossrate = {
        #                 "name": "lineloss",
        #                 "val": 0,
        #                 "timestamp": dateTimestamp()
        #             }
        #             bodyValue = [loss_val, lvEnergyAll,
        #                          meterEnergy, linelossrate]
        #         else:
        #             # print(((abs(a-dlmsKWH_adding))/a)*100)
        #             loss_val = {
        #                 "name": "lossVal",
        #                 "val": abs(LVEnergy-dlmsKWH_adding),
        #                 "timestamp": dateTimestamp()
        #             }
        #             lvEnergyAll = {
        #                 "name": "branchEnergy",
        #                 "val": LVEnergy,
        #                 "timestamp": dateTimestamp()
        #             }
        #             meterEnergy = {
        #                 "name": "meterEnergy",
        #                 "val": dlmsKWH_adding,
        #                 "timestamp": dateTimestamp()
        #             }
        #             lineLossFormula = ((abs(a-dlmsKWH_adding))/a)*100
        #             linelossrate = {
        #                 "name": "lineloss",
        #                 "val": lineLossFormula,
        #                 "timestamp": dateTimestamp()
        #             }
        #             bodyValue = [loss_val, lvEnergyAll,
        #                          meterEnergy, linelossrate]

        #         topic = 'huawei/0001/analysis/lineloss/'
        #         # print("Topic: %s" % topic)
        #         # print("Message: %s" % str(bodyValue))
        #         dictMessage = {}
        #         dictMessage["token"] = dateToken()
        #         dictMessage["timestamp"] = dateTimestamp()
        #         dictMessage["body"] = bodyValue

        #         dictSend = {}
        #         dictSend['topic'] = topic
        #         dictSend['message'] = dictMessage

        #         dictSendStr = str(dictSend['message']).replace("'", '"')
        #         clientmqtt.publish(topic, dictSendStr)
        #         dlmsKWH_adding = 0

                # print("LVKWH")
                # print(a)

    clientmqtt.subscribe('huawei/0001/DLMS/response/#')
    clientmqtt.subscribe('huawei/0001/LVMeter/#')
    clientmqtt.on_message = on_message


def run():
    client_mqtt = connect_mqtt()
    subscribe(client_mqtt)
    client_mqtt.loop_forever()


if __name__ == '__main__':
    run()
