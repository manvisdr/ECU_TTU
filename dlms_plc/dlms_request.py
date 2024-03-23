import serial

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


def read2(self):
    counter = 0
    dlechar = False
    msg_byte = b''
    message = []
    index = 0
    completeMsg = False
    while True:
        # if (self.serial.inWaiting() > 0):
        inChar = self.serial.read()
        # if completeMsg:
        #     break
        if inChar == b'\x68':
            while True:
                inChar = self.serial.read()
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
    return msg_byte


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


ser = serial.Serial('COM1', 115200)
for i in range(len(request_block)):
    destination = b'\x38\x00\x00\x19\x46\x02'
    command = make13762(destination, request_block[i])
    ser.write(command)
    read2()
