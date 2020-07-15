#!/usr/bin/python3
import operator
import sys, os
import json
import math
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
import pymongo
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from analysis.analysis_base import abase
from btc.payload import payload
from btc.btcclient import btcclient

#module name
name="aproofbase"

COINS = comm.values.COINS
class aproofbase(abase):

    def __init__(self, name = "aproofbase", dbconf = None, fdbconf = None, nodes = None, chain = "btc"):
        self._fdbclient = None
        super().__init__(name, None, nodes)
        self._dbclient = None
        self._fdbclient = None
        self._module = None
        self.__valid_txtype = []
        if dbconf is not None:
            self._dbclient = dbvproof(name, dbconf.get("host"), dbconf.get("db"), 
                    dbconf.get("user"), dbconf.get("password"), dbconf.get("authdb", "admin"), 
                    newdb = dbconf.get("newdb", True), rsname=dbconf.get("rsname", None))
        if fdbconf is not None:
            self._fdbclient = dbvfilter(name, fdbconf.get("host"), fdbconf.get("db"), 
                    fdbconf.get("user"), fdbconf.get("password"), fdbconf.get("authdb", "admin"), 
                    newdb = fdbconf.get("newdb", True), rsname=fdbconf.get("rsname"))

    def __del__(self):
        super().__del__()
        if self._fdbclient is not None:
            pass

    def stop(self):
        super().stop()

    def check_tran_is_valid(self, tran_info):
        prooftype = tran_info.get("type", "")
        return self.is_valid_prooftype(prooftype) and tran_info.get("valid")

    def get_opreturn_txids(self, index, limit = 10, sort = pymongo.ASCENDING):
        self._logger.debug("get_opreturn_txids(index={index})")
        coll = self._fdbclient.get_collection(self.collection.OPTRANSACTION.name.lower(), create = True)
        datas = coll.find({"_id":{"$gte":index}}, limit = limit)#.sort(["_id", sort])
        return datas

    @property
    def valid_txtype(self):
        return self.__valid_txtype

    def append_valid_txtype(self, txtype):
        self.__valid_txtype.append(txtype)

    def is_valid_prooftype(self, txtype):
        if self.valid_txtype is None or len(self.valid_txtype) == 0:
            return True

        return state in self.valid_txtype:

    def proofstate_name_to_value(self, name):
        return payload.state_name_to_value(name)

    def proofstate_value_to_name(self, value):
        return payload.state_value_to_name(value)

    def prooftype_name_to_value(self, name):
        return payload.type_name_to_value(name)

    def prooftype_value_to_name(self, value):
        return payload.type_value_to_name(value)

