# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.iostream
import socket
import binascii
import acpi
import asdu
import struct
import logging
from bitstring import ConstBitStream
from tornado.gen import Task, engine

LOG = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class IEC104Client(object):

    def __init__(self):
        self.socket = socket.socket()
        self.ssn = 0
        self.rsn = 0
        self.stream = tornado.iostream.IOStream(self.socket)

    def connect(self, ip, port=2404):
        self.stream.connect((ip, port), self.connect_callback)

    @engine
    def receive(self, data):
        start, length = struct.unpack('2B', data)
        print "len:", length
        data = yield Task(self.stream.read_bytes, length)
        s_acpi = ''.join(struct.unpack_from('4s', data))  # keep 0x00
        acpi_control = struct.unpack_from('B', data)[0]

        if acpi_control & 1 == 0:  # I-FRAME
            ssn, rsn = acpi.parse_i_frame(s_acpi)
            LOG.debug("ssn: {}, rsn: {}".format(ssn, rsn))
            s_asdu = ConstBitStream(bytes=data, offset=4*8)
            o_asdu = asdu.ASDU(s_asdu)

        elif acpi_control & 3 == 1:  # S-FRAME
            print "B"
            rsn = acpi.parse_s_frame(s_acpi)
            print rsn

        elif acpi_control & 3 == 3:  # U-FRAME
            print "A"
            if s_acpi == acpi.STARTDT_CON:
                print 'connected'

            if s_acpi == acpi.TESTFR_ACT:
                print 'ping'
                yield Task(self.send, acpi.TESTFR_CON)
        self.stream.read_bytes(2, self.receive)

    @engine
    def connect_callback(self):
        print "connect"
        LOG.debug("Send STARTDT_ACT")
        yield Task(self.send, acpi.STARTDT_ACT)
        self.stream.read_bytes(2, self.receive)

    def send(self, data, callback):
        self.stream.write("\x68" + struct.pack("B", len(data)) + data, callback)


if __name__ == "__main__":
    iec = IEC104Client()
    iec.connect('127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()