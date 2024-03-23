# standard libraries
import socket    # used for TCP/IP communication
import time      # used to insert current date in email report
import smtplib   # used to send email report
# from socket import *
# from select import *
# from string import *
import sys
from getopt import getopt, GetoptError

# nonstandard library
import serial


# class Connection:
#     "A connection is a class that forwards requests between TCP and Serial"

#     def __init__(self, socket, com):
#         self.socket = socket
#         self.com = com

#     def fileno(self):
#         "Required, look it up"
#         return self.socket.fileno()

#     def init_tcp(self):
#         "Set up the TCP connection and do telnet negotiation"

#         "telnet negotiation:  we don't want linemode"
#         "      COMMAND,   DONT,      linemode"
#         data = chr(255) + chr(254) + chr(34)
#         self.socket.send(data)

#         "telnet negotation:  we don't want local echo"
#         "      COMMAND,   DONT,      echo"
#         data = chr(255) + chr(254) + chr(1)
#         self.socket.send(data)

#         "send the header"
#         self.socket.send(
#             "************************************************\r\n")
#         self.socket.send("Telnet <--> Serial Bridge by Eli Fulkerson\r\n")
#         self.socket.send("http://www.elifulkerson.com for updates       \r\n")
#         self.socket.send("\r\n")
#         self.socket.send(
#             "This program uses non-standard python libraries:\r\n")
#         self.socket.send("   - pyserial by Chris Liechti\r\n")
#         self.socket.send("   - pywin32 by Mark Hammond (et al)\r\n")
#         self.socket.send("\r\n")
#         self.socket.send(
#             "************************************************\r\n")

#         self.socket.send("\r\n")
#         self.socket.send("You are now connected to %s.\r\n" % self.com.portstr)

#     def recv_tcp(self):
#         "Receive some data from the telnet client"
#         data = self.socket.recv(1024)
#         return data

#     def send_tcp(self, data):
#         "Send some data out to the telnet client"
#         self.socket.send(data)

#     def recv_serial(self):
#         "Recieve some data from the serial port"
#         data = self.com.read(self.com.inWaiting())
#         return data

#     def send_serial(self, data):
#         "Send some data out to the serial port"
#         # try:
#         #     if ord(data) == 3:
#         #         self.com.sendbreak()
#         # return
#         #     except:
#         #         pass
#         self.com.write(data)


# class Handler:
#     def __init__(self):
#         global LISTEN
#         global com

#         self.clist = []
#         self.tcpconnected = False
#         self.serialconnected = False

#         self.start_new_listener()

#     def start_new_listener(self):
#         self.listener = socket(AF_INET, SOCK_STREAM)
#         self.listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#         self.listener.bind(('', LISTEN))
#         self.listener.listen(32)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 4059))
sock.listen(5)

ser = serial.Serial("COM1", 9600)

counter = 0
dlechar = False
message = []
msg_bytes = b''
index = 0
completeMsg = False

while True:
    # if (self.serial.inWaiting() > 0):
    inChar = ser.read()
    # if completeMsg:
    #     break
    if inChar == b'\x68':
        while True:
            inChar = ser.read()
            # print(inChar)
            if inChar != b'\x16':
                message.append(inChar)
                msg_bytes += inChar
                index += 1
            else:
                print("completeMsg")
                completeMsg = True
                break

# else:
    if completeMsg:
        break

print(msg_bytes)
connection, address = sock.accept()
connection.send(msg_bytes)
