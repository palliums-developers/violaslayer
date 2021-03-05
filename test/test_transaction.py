#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc transactions and proof main
'''
import operator
import signal
import sys, os, time
sys.path.append(os.getcwd())
sys.path.append("..")
import traceback
import threading
import stmanage
import subprocess
import comm.values
from time import sleep, ctime
import comm.functions as fn
from comm.error import error
from comm.result import parse_except
from btc.btcclient import btcclient
from enum import Enum
from comm.parseargs import parseargs
from btc.payload import payload
from btc.transaction import transaction
from comm.functions import (
        json_reset, 
        json_print, 
        json_dumps
        )

COINS = comm.values.COINS

name="testtransaction"
def test_createrawtransaction():
        receiver_addr = "2N9gZbqRiLKAhYCBFu3PquZwmqCBEwu1ien"
        combin_addr = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB"
        sender_addr = "2MxBZG7295wfsXaUj69quf8vucFzwG35UWh" 
        pl = payload(name, stmanage.get_chain_id())
        toaddress = "cae5f8464c564aabb684ecbcc19153e9"
        sequence = 20200512001
        module = "e1be1ab8360a35a0259f1c93e3eac736"
        swap_type = "b2vusd"
        amount = 0.000002
        outamount = int(amount * 100000000) 
        times = 0

        print(f'''************************************************************************create ex start
        toaddress:{toaddress}
        sequence: {sequence}
        module:{module}
**********************************************************************************''')
        ret = pl.create_ex_start(swap_type, toaddress, sequence, module, outamount, times)
        assert ret.state == error.SUCCEED, f"payload create_ex_start.{ret.message}"
        data = ret.datas

        client = btcclient(name, stmanage.get_btc_conn())
        tran = transaction(name)
        tran.appendoutput(receiver_addr, 0.000001)
        tran.appendoutput(combin_addr, amount)
        tran.appendoutputdata(data)
        
        ret = tran.getoutputamount()
        assert ret.state == error.SUCCEED, ret.message
        print("output amount sum: {ret.datas * COINS}")

        ret = client.getaddressunspentwithamount(sender_addr, ret.datas * COINS)
        assert ret.state == error.SUCCEED, ret.message

        unspents = ret.datas
        for unspent in unspents:
            tran.appendinput(unspent.get("txid"), unspent.get("vout"))

        print(f"inputs: {tran.inputs}")
        print(f"outputs: {tran.outputs}")
        ret = client.createrawtransaction(tran.inputs, tran.outputs)
        assert ret.state == error.SUCCEED, ret.message

        privkeys = ["cUrpMtcfh4s9CRdPEA2tx3hYQGb5yy7pkWQNzaMBZc8Sj42g8YA8"]
        ret = client.signrawtransactionwithkey(ret.datas, privkeys)
        assert ret.state == error.SUCCEED, ret.message
        tran = ret.datas
        json_print(tran)
        print("*"*30)

        ret = client.estimatesmartfee(1)
        assert ret.state == error.SUCCEED, ret.message
        estimatefee = ret.datas

        print(f"estimatefee:{estimatefee}")

        ret = client.decoderawtransaction(tran.get("hex"))
        assert ret.state == error.SUCCEED, ret.message
        weight = ret.datas.get("weight")
        ret = client.getminfeerate(estimatefee, weight)
        print(f"transaction minfeerate:{ret.datas:.8f}")

def test_sendtoaddress():
        sender_addr = "2MxBZG7295wfsXaUj69quf8vucFzwG35UWh" 
        receiver_addr = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB"
        #receiver_addr = "2MyMHV6e4wA2ucV8fFKzXSEFCwrUGr2HEmY"
        combin_addr = "2MxBZG7295wfsXaUj69quf8vucFzwG35UWh"
        swap_type = payload.txtype.B2VM.name.lower()
        pl = payload(name, stmanage.get_chain_id())
        #toaddress = "5862a9e3e23737459299638e54b2ada3"
        toaddress = "0000000000000000004252472d425443"
        sequence = int(time.time())
        module = "00000000000000000000000000000001"
        amount = 0.001
        outamount = int(amount * 7 * 100_0000) 
        times = 0
        ret = pl.create_ex_start(swap_type, toaddress, sequence, module, outamount, times)
        assert ret.state == error.SUCCEED, f"payload create_ex_start.{ret.message}"
        data = ret.datas

        client = btcclient(name, stmanage.get_btc_conn())
        privkeys = ["cUrpMtcfh4s9CRdPEA2tx3hYQGb5yy7pkWQNzaMBZc8Sj42g8YA8"]
        ret = client.sendtoaddress(sender_addr, receiver_addr, amount, privkeys, data, subtractfeefromamount = True)
        assert ret.state == error.SUCCEED, f"sendtoaddress failed.{ret.message}"
        print(json_dumps(ret.to_json()))

def main():
    try:
        amounts = [1, 2, 3, 5, 8, 13, 21, 34, 36, 40, 50, 52, 100, 200]
        ret = btcclient.getamountlist(int(sys.argv[1]), list(amounts))
        print(f"list:{amounts}")
        print(f"use amount: {ret}")

    except Exception as e:
        parse_except(e)
    finally:
        print("end main")

def setup():
    stmanage.set_conf_env("../violaslayer.toml")

if __name__ == "__main__":
    setup()
    pa = parseargs(globals())
    pa.test(sys.argv)

