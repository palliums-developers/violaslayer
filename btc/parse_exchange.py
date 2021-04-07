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
address_len = 16

def __convert_to_str(value):
    return f"{value}"

def parse_ex_start(data):
    try:
        if len(data) != 51:
            return result(error.ARG_INVALID, f"start swap data len {len(data)} ({data.hex()}) is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len

        [sequence]= struct.unpack_from(">Q", data, data_offer)
        data_offer = data_offer + 8 + address_len
        [out_amount, times]= struct.unpack_from(">QH", data, data_offer)
        data_offer = data_offer + 8 + 2
        [chain_id]= struct.unpack_from(">B", data, data_offer)

        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "vtoken" : data[address_len + 8 : address_len + 8 + address_len].hex(),
                "out_amount" : out_amount,
                "times": times,
                "chain_id": chain_id
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_end(data):
    try:
        if len(data) != 41:
            return result(error.ARG_INVALID, f"end data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len

        [sequence, amount, version] = struct.unpack_from(">QQQ", data, data_offer)
        data_offer = data_offer + 8 + 8 + 8
        [chain_id]= struct.unpack_from(">B", data, data_offer)

        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "out_amount_real" : amount,
                "vheight" : version,
                "chain_id" : chain_id
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_cancel(data):
    try:
        if len(data) != 25:
            return result(error.ARG_INVALID, f"cancel data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len

        [sequence] = struct.unpack_from(">Q", data, data_offer)
        data_offer = data_offer + 8
        [chain_id]= struct.unpack_from(">B", data, data_offer)

        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "chain_id" : chain_id
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_stop(data):
    try:
        if len(data) != 25:
            return result(error.ARG_INVALID, f"stop data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len

        [sequence] = struct.unpack_from(">Q", data, data_offer)
        data_offer = data_offer + 8
        [chain_id]= struct.unpack_from(">B", data, data_offer)

        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "chain_id" : chain_id
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

def parse_ex_mark(data):
    try:
        if len(data) != 41:
            return result(error.ARG_INVALID, f"v2v mark data len{len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len
        [sequence, version, amount] = struct.unpack_from(">QQQ", data, data_offer)

        data_offer = data_offer + 8 + 8 + 8
        [chain_id]= struct.unpack_from(">B", data, data_offer)

        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "vheight" : version,
                "amount_real" : amount,
                "chain_id" : chain_id
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret
def parse_btc_mark(data):
    try:
        if len(data) < 24:
            return result(error.ARG_INVALID, f"btc mark data len {len(data)} is too small.")
        data_offer = 0

        #receiver address  32 Hex
        data_offer = data_offer + address_len

        [sequence, amount]= struct.unpack_from(">QQ", data, data_offer)
        data_offer = data_offer + 16 
        
        bname = struct.unpack_from(f"{len(data) - data_offer}s", data, data_offer)
        name = "".join([v.decode() for v in bname])
        datas = {
                "address": data[:address_len].hex(),
                "sequence" : __convert_to_str(sequence),
                "amount_real": amount,
                "name": name
                }

        ret = result(error.SUCCEED, datas = datas)
    except Exception as e:
        ret = parse_except(e)
    return ret

