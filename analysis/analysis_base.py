#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import hashlib
import traceback
import datetime
import sqlalchemy
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from db.dbv2b import dbv2b
from btc.btcclient import btcclient
from enum import Enum
from db.dbvbase import dbvbase
from baseobject import baseobject

#module name
name="abase"

COINS = comm.values.COINS
class abase(baseobject):
    #enum name must be transaction datas "type"
    #collect list
    ##  blockinfo     -block info       key = blockhash  ;  key = height
    ##  transaction   -rawtransaction   key = txid
    ##  txout         -transaction      key = txid + n
    ##  wallet        -addresses txout  key = address
    ##  exproof       -btc violas map   key = index (0~n)

    class txoutstate(Enum):
        NOUSE       = 1,
        USED        = 2

    class collection(Enum):
        BLOCKINFO   = 1,
        TRANSACTION = 2,
        TXOUT       = 3,
        WALLET      = 4,
        EXPROOF     = 5

    def __init__(self, name, dbconf, vnodes):
        baseobject.__init__(self, name)
        self._step = 1000
        self._min_valid_version = -1
        self._dbclient = None
        self._vclient = None
        self._connect_db(name, dbconf)
        self._connect_btc(name, vnodes)
        pass

    def __del__(self):
        if self._dbclient is not None:
            self._dbclient.save()

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host", "127.0.0.1"), rconf.get("port", 37017), rconf.get("db"), rconf.get("user", None), rconf.get("password", None), rconf.get("authdb", "admin"), rconf.get("newdb", True))
        return self._dbclient

    def _connect_btc(self, name, node):
        if node is not None:
            self._vclient = btcclient(name, node) 
        return self._vclient

    def set_min_valid_version(self, version):
        self._min_valid_version = version
        self._logger.debug(f"set min valid version {self.get_min_valid_version()}")

    def get_min_valid_version(self):
        self._logger.debug(f"get min valid version {self._min_valid_version}")
        return self._min_valid_version

    def get_start_version(self, version):
        return max(self.get_min_valid_version(), version)

    def stop(self):
        if self._vclient is not None:
            self._vclient.stop()
        self.work_stop()

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def create_tran_id(self, txid):
        return f"{txid}"

    def json_to_dict(self, data):
        try:
            data = json.loads(data)
            ret = result(error.SUCCEED, "", data)
        except Exception as e:
            ret = result(error.FAILED, "data is not json format.")
        return ret

    def parse_tran(self, transaction):
        try:
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

        
