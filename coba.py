import json
from paho.mqtt import client as mqtt_client
import time
from time import gmtime, strftime
import os

broker = '203.194.112.238'
port = 1883
topic = "huawei/0001/DaqoJc/notify/event/database/ADC/ADC_6536107f849fb0a4/#"
client_id = f'asdaas'
username = 'das'
password = 'mgi2022'


def subscribe(client: mqtt_client):

    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        client.subscribe(topic)
        client.on_message = on_message


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


#
successIndex = []

# def sendQueue():
#     global successIndex
#     with open('logFile.txt', "r") as fp:
#         lines = fp.readlines()
#         print(len(lines))
#         count = 0
#         for line in lines:
#             successIndex.append([line, count])
#             count += 1
#         print(successIndex)
#         print(successIndex[0][0])
#         # we want to remove 5th line

#         with open('logFile.txt', 'w') as fw:
#             for line in lines:
#                 if line != successIndex[0][0]:
#                     fw.write(line)
#         if line != successIndex[0][0]:
#             fp.write(line)


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
