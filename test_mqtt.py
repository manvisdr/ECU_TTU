import json
import time
from time import gmtime, strftime
import os
from paho.mqtt import client as mqtt_client
broker = '203.194.112.238'
port = 1883
topic = "huawei/0001/DaqoJc/notify/event/database/ADC/ADC_6536107f849fb0a4/#"
client_id = f'asda'
username = 'das'
password = 'mgi2022'
os.environ['TZ'] = 'Asia/Jakarta'
# time.tzset()

Watt_phsA = 0
Watt_phsB = 0
Watt_phsC = 0
start_time = 0
time_last = 0

kwhLast = 0
kwh = 0

pathFile = 'kwhLog.txt'
if os.path.isfile(pathFile):
    print('existing')
    f = open(pathFile, 'r')
    tempFile = f.readline()
    tempFile = tempFile.split('|')
    kwhLast = float(tempFile[0])
    kwhLast = round(kwhLast, 4)
    print("kwhLast: %f" % (kwhLast))
    f.close()
else:
    f = open(pathFile, 'x')
    f.close()
    kwhLast = 0

kwh = kwhLast
print("EXiSTING KWH %f" % (kwh))
counter = 0


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


def subscribe(client: mqtt_client):

    def on_message(client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}")
        # global start_time
        # global time_last
        # global kwh
        # start_time = time.time()

        currentData = msg.payload.decode()
        currentData = json.loads(currentData)
        # # print(currentData['body'])
        for v in currentData['body']:
            if v['name'] == 'PhV_phsA':
                # global Watt_phsA
                # Watt_phsA = float(v['val'])
                # print('PhV_phsA')
                # print(v['val'])
                # print(v['timestamp'])
                print('PhV_phsA || %s || %s' % (v['val'], v['timestamp']))
            if v['name'] == 'PhV_phsB':
                # print('PhV_phsB')
                # print(v['val'])
                # print(v['timestamp'])
                print('PhV_phsB || %s || %s' % (v['val'], v['timestamp']))
                # global Watt_phsB
                # Watt_phsB = float(v['val'])
            if v['name'] == 'PhV_phsC':
                print('PhV_phsC || %s || %s' % (v['val'], v['timestamp']))
                # print(v['val'])
                # print(v['timestamp'])
            if v['name'] == 'Hz':
                print('Hz || %s || %s' % (v['val'], v['timestamp']))
            # if v['name'] == 'PhV_phsC':
            #     print('PhV_phsC %f %s' % (v['val'], v['timestamp']))
            # if v['name'] == 'PhV_phsC':
            #     print('PhV_phsC %f %s' % (v['val'], v['timestamp']))

        # print(start_time)
        # dt = start_time - time_last
        # print('ELAPSED: %f' % (dt))
        # all_watts = (Watt_phsA + Watt_phsB + Watt_phsC)
        # kwh += all_watts * dt / 3600000
        # print('KWH: %f' % (kwh))
        # time_last = start_time
        # counter += 1

        # if counter == 10:
        #     # result = client.publish('test', '%.3f' % kwh)
        #     # status = result[0]
        #     status = 1

        #     time_ns = time.time_ns()
        #     time_now = int(time.time())
        #     time_ns = str(time_ns).replace(str(time_now), "")
        #     ts = str(time_now) + "_"+str(time_ns)
        #     time_str = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        #     print(time_str)

        #     if status != 0:
        #         with open(pathFile, 'w') as f:
        #             f.write(str(kwh)+'|'+ts)
        #             # +'|'+time_str+"\n"
        #             # f.write("text to write\r\n")
        #         f.close()
        #     counter = 0

    # print(currentData['body'])
    client.subscribe(topic)
    client.on_message = on_message


def sendQueueKwh():
    f = open(pathFile, 'a')
    msg = f.readline()
    print(msg)
    f.close()


mqttConnect = 1


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()

# time = 0
# samples = [[0, 1350]]
# for i in range(0, 200):
#     samples.append([time+30, 1400])
#     samples.append([time+60, 1350])
#     time += 60

# n_samples = len(samples)
# print(samples)

# # METHOD 1
# total_ws = 0.0
# total_t = 0
# for i in range(1, n_samples):
#     dt = samples[i][0] - samples[i-1][0]
#     average = (samples[i][1] + samples[i-1][1]) / 2
#     total_ws += average * dt
#     total_t += dt
# print("Total ws: %0.2f" % total_ws)
# print("Total w: %0.2f" % (total_ws/total_t))
