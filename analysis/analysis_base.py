#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
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
from btc.btcclient import btcclient
from enum import Enum
from db.dbvfilter import dbvfilter
from baseobject import baseobject
from btc.payload import payload

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
        NOUSE       = 1
        USED        = 2

    class collection(Enum):
        BLOCKINFO   = 1
        TRANSACTION = 2
        TXOUT       = 3
        WALLET      = 4
        EXPROOF     = 5
        OPTRANSACTION = 6

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
            pass

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host", "127.0.0.1:37017"), rconf.get("db"), rconf.get("user", None), rconf.get("password", None), rconf.get("authdb", "admin"), newdb = rconf.get("newdb", True), rsname=rconf.get("rsname", None))
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
        return int(max(self.get_min_valid_version(), version))

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

    def create_tran_id(self, address, sequence):
        return f"{txid}_{sequence}"

    def json_to_dict(self, data):
        try:
            data = json.loads(data)
            ret = result(error.SUCCEED, "", data)
        except Exception as e:
            ret = result(error.FAILED, "data is not json format.")
        return ret

    def parse_tran(self, tran):
        try:
            datas = {\
                    "create_block": tran.get("blockhash"), 
                    "update_block": tran.get("blockhash"),
                    "state":,
                    "address":None,
                    "vtoken":None,
                    "num_btc":None,
                    "issuer":None, 
                    "receiver":None, 
                    "sequence":None,
                    "type":None,
                    "index":0
                    }

            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

    def create_txout_id(self, txid, n):
        return f"{txid}_{n}"

    def is_allow_inputtype(self, scrpittype):
        #nonstandard  pubkey pubkeyhash scripthash multisig nulldata witness_v0_keyhash witness_v0_scripthash witness_unknown
        return scrpittype in ["scripthash", "witness_v0_keyhash", "witness_v0_scripthash", "pubkeyhash"]

    def is_allow_outputtype(self, scrpittype):
        #nonstandard  pubkey pubkeyhash scripthash multisig nulldata witness_v0_keyhash witness_v0_scripthash witness_unknown
        return scrpittype in ["scripthash", "witness_v0_keyhash", "witness_v0_scripthash", "pubkeyhash"]
        
