#!/usr/bin/python3
# -*- coding: utf-8 -*-

import operator
import sys, os
import json, decimal
sys.path.append(os.getcwd())
sys.path.append("..")
import comm
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from comm.functions import json_print, json_dumps, json_reset
import btc.parse_exchange as parse_exchange
import btc.create_exchange as create_exchange
from enum import Enum
from ctypes import create_string_buffer
from comm.parseargs import parseargs
from btc.payload import payload

#module name
name="payloadtest"
#start
    ###txid: f30a9f9497b97aa5f95a46f1bd6fceeb26241686526068c309dee8d8fafc0a97
    ###to_address:f086b6a2348ac502c708ac41d06fe824c91806cabcd5b2b5fa25ae1c50bed3c6 
    ###sequence: 20200110006
    ###token:cd0476e85ecc5fa71b61d84b9cf2f7fd524689a4f870c46d6a5d901b5ac1fdb2
   
#end (manual create, can't found txid)

#btc_mark (manual create, can't found txid)
opstr_btc_mark = "6a3176696f6c617300031030c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6000000000000271076696f6c617300"
def check(src, dest):
    return src == dest

def get_payload_cli(chain_id):
    return payload(name, chain_id)

def test_parse_start():
    opstr = "6a3c76696f6c617300043000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb20000000000000000000004"
    pdata = get_payload_cli(4)
    ret = pdata.parse(opstr)
    check_result_is_valid(ret)

def test_parse_start_version_is_invalid():
    opstr = "6a3c76696f6c617300033000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb20000000000000000000004"
    pdata = get_payload_cli(4)
    ret = pdata.parse(opstr)
    check_result_is_invalid(ret)

def test_create_start():
    target = "76696f6c617300044000c91806cabcd5b2b5fa25ae1c50bed3c60000000001343c3fe1be1ab8360a35a0259f1c93e3eac73600000000000186a0007b04"
    toaddress = "c91806cabcd5b2b5fa25ae1c50bed3c6"
    sequence = 20200511
    module = "e1be1ab8360a35a0259f1c93e3eac736"
    outamount = 100000
    chain_id = 4
    times = 123
    pl = get_payload_cli(4)
    ret = pl.create_ex_start(payload.txtype.B2VUSD.name.lower(), toaddress, sequence, module, outamount, times)
    assert ret.state == error.SUCCEED, "payload create_ex_start.{ret.message}"

    assert ret.datas == target, "create result datas != target datas"
    ret = pl.parse_opt_datahex(ret.datas)
    check_result_is_valid(ret)

#data valid value is true
def check_result_is_valid(ret, versions = None):
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed.{} data = {}".format(ret.message, ret.datas)
    assert ret.datas.get("valid", False), "valid not true,, version is {} data = {}".format(ret.datas.get('version'), ret.datas) 

#data valid value is false
def check_result_is_invalid(ret, versions = None):
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed.{} data = {}".format(ret.message, ret.datas)
    assert not ret.datas.get("valid"), "valid not false, datas = {}".format(ret.datas) 

def test_np():
    pdata = get_payload_cli(4)

    opstr_start = "6a3d76696f6c617300043000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb20000000000000000000004"
    ret = pdata.parse(opstr_start)
    check_result_is_valid(ret)
    
    opstr_start = "6a3d76696f6c617300033000c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb20000000000000000000004"
    ret = pdata.parse(opstr_start)
    check_result_is_invalid(ret)

    opstr_end = "6a2376696f6c617300043003c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b604"
    ret = pdata.parse(opstr_end)
    check_result_is_valid(ret)

    opstr_end = "6a2376696f6c617300033003c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b604"
    ret = pdata.parse(opstr_end)
    check_result_is_invalid(ret)

    opstr_b2v_stop = "6a2376696f6c617300043003c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b604"
    ret = pdata.parse(opstr_b2v_stop)
    check_result_is_valid(ret)

    opstr_btc_mark = "6a3176696f6c617300041030c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6000000000000271076696f6c61730004"
    ret = pdata.parse(opstr_btc_mark)
    check_result_is_valid(ret)

    opstr_b2veur_start = "6a3c76696f6c617300044010c91806cabcd5b2b5fa25ae1c50bed3c600000004b40537b6524689a4f870c46d6a5d901b5ac1fdb20000000000002710000004"
    ret = pdata.parse(opstr_b2veur_start)
    check_result_is_valid(ret)


def show_info(title = "", **kwargs):
    print(title)
    print(kwargs)

def test_exchange():
    toaddress = "c91806cabcd5b2b5fa25ae1c50bed3c6"
    sequence = 20200511
    module = "e1be1ab8360a35a0259f1c93e3eac736"
    outamount = 100000
    chain_id = 4
    times = 123
    show_info('create ex start', toaddress=toaddress, sequence=sequence, module=module, outammount=outamount, times=times)

    ret = create_exchange.create_ex_start(toaddress, sequence, module, outamount, times, chain_id)
    ret = parse_exchange.parse_ex_start(ret.datas)
    json_print(ret.datas)
    
    amount = 100010
    version = 123456
    show_info("create ex end", toaddress=toaddress, sequence=sequence, amount=amount, version=version)

    ret = create_exchange.create_ex_end(toaddress, sequence, amount, version, chain_id)
    ret = parse_exchange.parse_ex_end(ret.datas)
    json_print(ret.datas)
    
    show_info('create ex cancel', toaddress=toaddress, sequence=sequence)

    ret = create_exchange.create_ex_cancel(toaddress, sequence, chain_id)
    ret = parse_exchange.parse_ex_cancel(ret.datas)
    json_print(ret.datas)

    show_info('create ex stop', toaddress=toaddress, sequence=sequence)

    ret = create_exchange.create_ex_stop(toaddress, sequence, chain_id)
    ret = parse_exchange.parse_ex_stop(ret.datas)
    json_print(ret.datas)

    proofname = "btcmark"
    show_info('create btc mark', toaddress=toaddress, sequence=sequence, amount=amount, name=proofname)

    ret = create_exchange.create_btc_mark(toaddress, sequence, amount, proofname)
    ret = parse_exchange.parse_btc_mark(ret.datas)
    json_print(ret.datas)

def test_payload():
    pl = get_payload_cli(4)
    toaddress = "cae5f8464c564aabb684ecbcc19153e9"
    sequence = 20200511
    module = "e1be1ab8360a35a0259f1c93e3eac736"
    outamount = 100000
    times = 123
    chain_id = 4
    show_info('create ex start', toaddress=toaddress, sequence=sequence, module=module, outammount=outamount, times=times)

    ret = pl.create_ex_start(payload.txtype.B2VUSD.name.lower(), toaddress, sequence, module, outamount, times)
    assert ret.state == error.SUCCEED, "payload create_ex_start.{ret.message}"
    ret = pl.parse_opt_datahex(ret.datas)
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed."
    

    amount = 100010
    version = 123456
    show_info('create ex end', toaddress=toaddress, sequence=sequence, amount=amount, version=version)

    ret = pl.create_ex_end(payload.txtype.B2VUSD.name.lower(), toaddress, sequence, amount, version)
    assert ret.state == error.SUCCEED, "payload create_ex_end."
    ret = pl.parse_opt_datahex(ret.datas)
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed."
    
    
    show_info('create ex cancel', toaddress=toaddress, sequence=sequence)

    ret = pl.create_ex_cancel(payload.txtype.B2VUSD.name.lower(), toaddress, sequence)
    assert ret.state == error.SUCCEED, "payload create_ex_cancel."
    ret = pl.parse_opt_datahex(ret.datas)
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed."

    proofname = "btcmark"
    show_info('create btc mark', toaddress=toaddress, sequence=sequence, amount=amount, name=proofname)

    ret = pl.create_btc_mark(payload.txtype.B2VUSD.name.lower(), toaddress, sequence, amount, proofname)
    assert ret.state == error.SUCCEED, "payload create_btc_mark."
    ret = pl.parse_opt_datahex(ret.datas)
    assert ret.state == error.SUCCEED, "parse OP_RETURN failed."


if __name__ == "__main__":
    pa = parseargs(globals())
    pa.test(sys.argv)
