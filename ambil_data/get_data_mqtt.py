import time
import paho.mqtt.client as mqttClient
import json

Connected = False  # global variable for the state of the connection

broker_address = "192.168.1.104"
port = 1883
user = "yourUSer"
password = "yourPass"


topicADCSet = 'Daqo104/get/request/database/realtime'
topicADCValue = 'DaqoJc/notify/event/database/ADC/ADC_6536107f849fb0a4'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    if message.topic == topicADCSet:
        d = json.loads(message.payload)
        for key, value in d['body'].items():
            print(value)
    elif message.topic == topicADCValue:
        d = json.loads(message.payload)
        for value in d['body']:
            print("%s: %s" % (value['name'], value['val']))
    # print(d['body'])


# def parse

client = mqttClient.Client("mgi-mel")  # create new instance
# client.username_pw_set(user, password=password)    #set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message


client.connect(broker_address, port=port)  # connect to broker
client.loop_start()  # start the loop

while Connected != True:  # Wait for connection
    time.sleep(0.1)

client.subscribe("DaqoJc/notify/event/database/ADC/ADC_6536107f849fb0a4")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
