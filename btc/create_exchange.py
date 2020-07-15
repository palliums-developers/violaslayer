#!/usr/bin/python3
# -*- coding: utf-8 -*-

import operator
import sys, os
import json, decimal
import struct, array
import numpy as np
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from comm.functions import json_print
from enum import Enum
from ctypes import create_string_buffer

#module name
name="createex"
def create_ex_start(toaddress, sequence, module):
    try:
        btoaddress = bytes.fromhex(toaddress)
        bmodule = bytes.fromhex(module)
        datas = create_string_buffer(len(btoaddress) + 8 + len(bmodule))

        data_offer = 0
        struct.pack_into(f">{len(btoaddress)}sQ{len(bmodule)}s", datas, data_offer, btoaddress, sequence, bmodule)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def create_ex_end(toaddress, sequence, amount, version):
    try:
        btoaddress = bytes.fromhex(toaddress)
        datas = create_string_buffer(len(btoaddress) + 8 + 8 + 8)

        data_offer = 0
        struct.pack_into(f">{len(btoaddress)}sQQQ", datas, data_offer, btoaddress, sequence, amount, version)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def create_ex_cancel(toaddress, sequence):
    try:
        btoaddress = bytes.fromhex(toaddress)
        datas = create_string_buffer(len(btoaddress) + 8)

        data_offer = 0
        struct.pack_into(f">{len(btoaddress)}sQ", datas, data_offer, btoaddress, sequence)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def create_ex_stop(toaddress, sequence):
    try:
        btoaddress = bytes.fromhex(toaddress)
        datas = create_string_buffer(len(btoaddress) + 8)

        data_offer = 0
        struct.pack_into(f">{len(btoaddress)}sQ", datas, data_offer, btoaddress, sequence)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def create_ex_mark(toaddress, sequence, version, amount):
    try:
        btoaddress = bytes.fromhex(toaddress)
        datas = create_string_buffer(len(btoaddress) + 8 + 8 + 8)

        data_offer = 0
        struct.pack_into(f">{len(btoaddress)}sQQQ", datas, data_offer, btoaddress, sequence, version, amount)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def create_btc_mark(toaddress, sequence, amount, name):
    try:
        btoaddress = bytes.fromhex(toaddress)
        bname = str.encode(name)
        datas = create_string_buffer(len(btoaddress) + 8 + 8 + len(bname))

        data_offer = 0
        print(bname)
        struct.pack_into(f">{len(btoaddress)}sQQ{len(bname)}s", datas, data_offer, btoaddress, sequence, amount, bname)

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

