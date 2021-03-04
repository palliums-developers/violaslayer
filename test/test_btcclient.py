#!/usr/bin/python3
# coding default python2.x : ascii   python3.x :UTF-8
# -*- coding: UTF-8 -*-
'''
btc transactions and proof main
'''
import operator
import signal
import sys, os
sys.path.append(os.getcwd())
sys.path.append("..")
import traceback
import log
import log.logger
import threading
import stmanage
import subprocess
from time import sleep, ctime
import comm.functions as fn
from comm.error import error
from comm.result import parse_except
from btc.btcclient import btcclient
from enum import Enum
from comm.functions import json_print
from comm.parseargs import parseargs

name="testbtcclient"

logger = log.logger.getLogger(name)
class CheckState:
    def __init__(self):
        self.__state = {"succeed":0, "failed":0, "count": 0}
    def update(self, state):
        if state == True:
            self.__state["succeed"] = self.__state.get("succeed", 0) + 1 
        else:
            self.__state["failed"] = self.__state.get("failed", 0) + 1 
    def info(self):
        self.__state["count"] = self.__state.get("succeed", 0) + self.__state.get("failed", 0)
        return self.__state

def setup():
    stmanage.set_conf_env("../violaslayer.toml")

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def check_result(ret, getvalue, fixvalue):
    if ret.state != error.SUCCEED:
        return False
    if fixvalue is not None and getvalue != fixvalue:
        return False

    return True

def test_btc():

    teststate = CheckState()
    client = getbtcclient()
    ret = client.getblockcount()
    ok = check_result(ret, ret.datas, None)

    ret = client.getblockhash(1612035)
    ok = check_result(ret, ret.datas, "0000000000000023d5e211d6681218cfbd39c97dc3bf21dd1b1d226d4af23688")
    teststate.update(ok)

    ret = client.getblockwithhash("0000000000000023d5e211d6681218cfbd39c97dc3bf21dd1b1d226d4af23688")
    ok = check_result(ret, ret.datas.get("merkleroot"), '732ba393120e497810db7ee33be2b595af82bc58c4e878e286761fbd363d5b3e')
    teststate.update(ok)

    ret = client.getblockwithindex(1612035)
    ok = check_result(ret, ret.datas.get("merkleroot"), '732ba393120e497810db7ee33be2b595af82bc58c4e878e286761fbd363d5b3e')
    teststate.update(ok)

    ret = client.getblocktxidswithhash("0000000000000023d5e211d6681218cfbd39c97dc3bf21dd1b1d226d4af23688")
    ok = check_result(ret, ret.datas[0], '9d6e259a2c07cb018b4338120ef826e2a5d7e1ae20ae221a699773bb568b4a14')
    teststate.update(ok)

    ret = client.getblocktxidswithindex(1612035)
    ok = check_result(ret, ret.datas[0], '9d6e259a2c07cb018b4338120ef826e2a5d7e1ae20ae221a699773bb568b4a14')
    teststate.update(ok)

    #9c3fdd8a5f9dff6fbd2c825650559d6180ee8eaf1938632e370d36f789984a35
    ret = client.getrawtransaction('9c3fdd8a5f9dff6fbd2c825650559d6180ee8eaf1938632e370d36f789984a35')
    ok = check_result(ret, ret.datas.get('hash'), 'ebf41472ebcc0a5d2636f08054974bd86f051d07f9121243a5fc5c225a53ed57')
    teststate.update(ok)
    json_print(teststate.info())

if __name__ == "__main__":
    pa = parseargs(globals())
    pa.test(sys.argv)
