import serial


header = b'\x68'  # Frame header
frame_length = b'\x45\00'  # 3762 frame length
control_word = b'\x41'
information_field = b'\x04\x00\xff\x00\x00'  # Information field
frame_serial_number = b'\x83'  # 3762 frame serial number
# source_address = b'\x01\x00\x01\x30\x02\x29'  # Source address
source_address = b'\x36\x01\x00\x00\x00\x00'
# Destination address: indicates the address of the table to be read
destination_addres = b'\x21\x00\x00\x19\x46\x02'  # meter 1
# destination_addres = b'\x38\x00\x00\x19\x46\x02'  # meter 2
function = b'\x13\x02\x00'  # AFN=13, Fn=2, means：Meter readig
# Communication protocol type: transparent transmission
transparent_protocol = b'\x00'
# packet_content = b'\x00\x01\x00\x10\x00\x01\x00\x1f\x60\x1d\xa1\x09\x06\x07\x60\x85\x74\x05\x08\x01\x01\xbe\x10\x04\x0e\x01\x00\x00\x00\x06\x5f\x1f\x04\x00\x00\x7e\x1f\xff\xff'  # Packet content
# packet_content = b'\x00\x01\x00\x10\x00\x01\x00\x1F\x60\x1D\xA1\x09\x06\x07\x60\x85\x74\x05\x08\x01\x01\xBE\x10\x04\x0E\x01\x00\x00\x00\x06\x5F\x1F\x04\x00\x00\x1E\x5D\xFF\xFF'
# packet_content = b'\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x01\x00\x00\x60\x01\x01\xFF\x02\x00'
packet_content = b'\x00\x01\x00\x10\x00\x01\x00\x0D\xC0\x01\xC1\x00\x03\x01\x00\x20\x07\x00\xFF\x02\x00'
packet_length = len(packet_content).to_bytes(1, 'big') + \
    b'\x00'  # The packet length is 2 bytes [2700]
# checksum = b'\xb3'  # Frame checksum
frame_end = b'\x16'  # Frame end
print(len(packet_content))

a = control_word+information_field+frame_serial_number + source_address+destination_addres+function + \
    transparent_protocol+packet_length+packet_content

aa = 0
for i in range(len(a)):
    # print(a[i])
    aa += int(a[i])
    # print(aa)

crc = aa & 0xFF

crc_bytes = crc.to_bytes(1, 'big')
# print(crc_bytes)

command = header+frame_length+control_word+information_field+frame_serial_number + source_address+destination_addres+function + \
    transparent_protocol+packet_length+packet_content+crc_bytes+frame_end
print(command)
ser = serial.Serial('COM1', 115200)
ser.write(command)
# print(ser.read())
