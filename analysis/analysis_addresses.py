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
        self._dbclient.use_collection("addresses")
        self.__split_count = 100

    def __del__(self):
        abase.__del__(self)

    def stop(self):
        abase.stop(self)
        self.work_stop()

    def create_address_id(self, info):
        return f"{info.get('address')}-{info.get('index')}"

    def get_address_info(self, address):
        try:
            ret  = self._dbclient.find_with_id(address)
            if ret.state != error.SUCCEED:
                return ret
            info = ret.datas
            split_count = info.get("split_count", self.__split_count)
            count = info.get("count", 0)
            maxindex=info.get("maxindex", 0) #now no-use
            index = (count) // (split_count)
            datas = {"address": address,\
                    "count":count,\
                    "index":index,\
                    "split_count":split_count,
                    }
            ret = result(error.SUCCEED, "", datas)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_address_keys(self, address, info):
        try:
            self._dbclient.update_with_id(address, {"split_count":info.get("split_index", self.__split_count), "count":info.get("count", 0) + 1, "maxindex": info.get("index") })
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_address_txout(self, txid, txout, blockhash):
        try:
            with self._dbclient.start_session(causal_consistency=True) as session:
                with session.start_transaction():
                    for vout in txout:
                        data = {}
                        ret = self._vclient.parsevout(vout)
                        if ret.state != error.SUCCEED:
                            return ret
                        voutfmt = ret.datas
                        addresses = voutfmt.get("addresses")
                        if addresses is not None and len(addresses) > 0:
                            self._logger.debug(f"txout addresses:{addresses}")
                            for address in addresses:
                                ret = get_address_info(address)
                                if ret.state != error.SUCCEED:
                                    return ret
                                info = ret.datas
                                id = self.create_address_id(info)

                                self._dbclient.push({"_id":id}, \
                                     {"txout": {"value":voutfmt.get("value", 0.0), "n":voutfmt.get("n"), "txid":txid}}, upsert = True)

                                self.update_address_keys(address, info)


        except Exception as e:
            ret = parse_except(e)
        return ret

