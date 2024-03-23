import serial
import socket


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
    print(len(packet_content))
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


destination = b'\x38\x00\x00\x19\x46\x02'
dlms_data = b'\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x02\x00'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 4059))
sock.listen(5)

command = make13762(destination, dlms_data)
print(command)
ser = serial.Serial('COM1', 115200)
ser.write(command)
# print(ser.read())
