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

#module name
name="parseex"
def parse_ex_start(data):
    try:
        if len(data) != 72:
            return result(error.ARG_INVALID, f"data len(len(data)) is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + 32

        [sequence]= struct.unpack_from(">Q", data, data_offer)
        data_offer = data_offer + 8

        datas = {
                "to_address": data[:32].hex(),
                "sequence" : sequence,
                "token" : data[data_offer:].hex()
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_end(data):
    try:
        if len(data) != 56:
            return result(error.ARG_INVALID, f"data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + 32

        [sequence, amount, version] = struct.unpack_from(">QQQ", data, data_offer)

        datas = {
                "to_address": data[:32].hex(),
                "sequence" : sequence,
                "amount" : amount,
                "version" : version
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_cancel(data):
    try:
        if len(data) != 40:
            return result(error.ARG_INVALID, f"data len(len(data)) is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + 32

        [sequence] = struct.unpack_from(">Q", data, data_offer)
        data_offer = data_offer + 8

        datas = {
                "to_address": data[:32].hex(),
                "sequence" : sequence,
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_mark(data):
    try:
        if len(data) != 56:
            return result(error.ARG_INVALID, f"data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + 32

        [sequence, version, amount] = struct.unpack_from(">QQQ", data, data_offer)

        datas = {
                "to_address": data[:32].hex(),
                "sequence" : sequence,
                "version" : version,
                "amount" : amount,
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret
def parse_btc_mark(data):
    try:
        if len(data) < 40:
            return result(error.ARG_INVALID, f"data len(len(data)) is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + 32

        [sequence, amount]= struct.unpack_from(">QQ", data, data_offer)
        data_offer = data_offer + 16 
        
        bname = struct.unpack_from(f"{len(data) - data_offer}s", data, data_offer)
        name = "".join([v.decode() for v in bname])
        datas = {
                "to_address": data[:32].hex(),
                "sequence" : sequence,
                "amount": amount,
                "name": name
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

