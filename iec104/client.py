# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.iostream
import socket
import binascii
import acpi
import asdu
import struct


class IEC104Client(object):

    def __init__(self):
        self.s = socket.socket()
        self.ssn = 0
        self.rsn = 0
        self.stream = tornado.iostream.IOStream(self.s)

    def connect(self, ip, port=2404):
        self.stream.connect((ip, port), self.connect_callback)

    def read(self, data):
        print binascii.hexlify(data)

        start, length, control_type = struct.unpack_from("<3B", data)

        control_fields = ''.join(struct.unpack_from("<ssss", data, 2))

        if control_type & 1 == 0:  # I-FRAME
            ssn, rsn = acpi.parse_i_frame(control_fields)
            print ssn, rsn
            print asdu.parse(data[6:])
        elif control_type & 3 == 1:  # S-FRAME
            rsn = acpi.parse_s_frame(control_fields)
            print rsn
        elif control_type & 3 == 3:  # U-FRAME
            if data == acpi.STARTDT_CON:
                print 'connected'

            if data == acpi.TESTFR_ACT:
                print 'ping'
                self.stream.write(acpi.TESTFR_CON)
        self.stream.read_bytes(6*8, None, self.read)

    def connect_callback(self):
        self.stream.write(acpi.STARTDT_ACT)
        self.stream.read_bytes(2, None, self.read)


if __name__ == "__main__":

    iec = IEC104Client()
    iec.connect('127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()