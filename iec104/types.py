# -*- coding: utf-8 -*-
from datetime import datetime


def cp56timebcd(buf):
    pass


def cp56time2a_to_time(buf):
    microsecond = (buf[1] & 0xFF) << 8 | (buf[0] & 0xFF)
    microsecond %= 1000
    second = int(microsecond)
    minute = buf[2] & 0x3F
    hour = buf[3] & 0x1F
    day = buf[4] & 0x1F
    month = (buf[5] & 0x0F) - 1
    year = (buf[6] & 0x7F) + 2000

    return datetime(year, month, day, minute, hour, second, microsecond)
