#!/usr/bin/python3
import operator
import sys, os
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import log
import hashlib
import traceback
import datetime
import sqlalchemy
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from analysis.analysis_base import abase
#module name
name="addresses"

COINS = comm.values.COINS
#load logging
    
class addresses(abase):
    def __init__(self, name = "addresses", dbconf = None, vnodes = None):
        abase.__init__(self, name, dbconf, vnodes) #no-use defalut db

    def __del__(self):
        abase.__del__(self)

    def stop(self):
        abase.stop(self)
        self.work_stop()

    def save_address_txout_(self, txid, txout, blockhash):
        try:
            for vout in txout:
                data = {}
                ret = self._vclient.parsevout(vout)
                if ret.state != error.SUCCEED:
                    return ret
                voutfmt = ret.datas
                addresses = voutfmt.get("addresses")
                if addresses is not None and len(addresses) > 0:
                    for address in addresses:
                        coll = self._dbclient.get_collection(address, create = True)
                        coll.save({"_id":self.create_txout_id(txid, voutfmt.get("n")), "value":voutfmt.get("value", 0.0), "n":voutfmt.get("n"), "txid":txid, "blockhash":blockhash})

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_address_txout(self, txid, txout, blockhash):
        try:
            coll = self._dbclient.get_collection("addresses", create = True)
            for vout in txout:
                data = {}
                ret = self._vclient.parsevout(vout)
                if ret.state != error.SUCCEED:
                    return ret
                voutfmt = ret.datas
                addresses = voutfmt.get("addresses")
                if addresses is not None and len(addresses) > 0:
                    for address in addresses:
                        print(address)
                        coll.update({"_id":address}, \
                                {"$push":{"txout": {"value":voutfmt.get("value", 0.0), "n":voutfmt.get("n"), "txid":txid, "blockhash":blockhash}}}, upsert = True)

        except Exception as e:
            ret = parse_except(e)
        return ret

