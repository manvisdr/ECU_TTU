import serial
import dlt645


ser = serial.Serial(
    "COM4",
    baudrate=2400,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# station_addr = dlt645.get_addr(ser)

# requesting active energy
frame = dlt645.Frame('000000000136')
frame.data = "00000000"
ser.write(frame.dump())
framedata = dlt645.read_frame(dlt645.iogen(ser))
# the data will be the full payload (energy valu and data identification)
print(framedata.data)

# shorthand function to directly get the active energy value
dlt645.get_active_energy('000000000136', ser)
