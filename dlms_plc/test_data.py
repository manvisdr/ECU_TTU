# # \x68\x33\x00\x41\x04\x00\xFF\x00\x00\x83\x36\x01\x00\x00\x00\x00\x21\x00\x00\x19\x46\x02\x13\x02\x00\x00\x15\x00\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x03\x00\x78\x16
# import json
# import binascii
# jsonFileName = 'D:\Documents\VSCode\SmartTTU\dlms_plc\kwh_list.json'
# jsonFile = open(jsonFileName, 'r')
# jsonFileLoad = json.loads(jsonFile.read())

# meterConf = []
# for v in jsonFileLoad:
#     meterConf.append(v)
# print(meterConf)
# listMeter1Phasa = []
# listMeter3Phasa = []
# for i in meterConf:
#     for v in i['serialNumber']:
#         if i['type'] == 1:
#             listMeter1Phasa.append(bytes.fromhex(v)[::-1])
#         if i['type'] == 3:
#             listMeter3Phasa.append(bytes.fromhex(v)[::-1])

# print(listMeter1Phasa)
# print(listMeter3Phasa)


# def str2bytes(string):
#     return "".join(chr(int(string[i:i+2], 16)) for i in range(0, len(string), 2))


# # a = "024619000021"
# # update_mac1 = bytes.fromhex(a)[::-1]
# # print(type(update_mac1))
# print(''.join(f'\\x{c:02x}' for c in listMeter1Phasa[0]))

import os
aa = 'test'
os.system('mosquitto_pub -m '+aa+'-t test/DLMS')
