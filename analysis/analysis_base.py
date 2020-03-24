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
from analysis.analysis_record import record

#module name
name="abase"

COINS = comm.values.COINS
class abase(baseobject):
    #enum name must be transaction datas "type"
    class datatype(Enum):
        V2B = 1
        B2V = 2
        UNKOWN = 255

    class trantype(Enum):
        violas    = 1
        UNKOWN = 255

    def __init__(self, name, ttype, dtype, dbconf, vnodes):
        baseobject.__init__(self, name)
        self._step = 1000
        self.__dtypes = []
        self._tran_types = []
        self._min_valid_version = -1
        self._dbclient = None
        self._vclient = None
        self._connect_db(name, dbconf)
        self._connect_btc(name, vnodes)

        self.append_data_type(dtype)
        self.append_tran_type(ttype)
        pass

    def __del__(self):
        if self._dbclient is not None:
            self._dbclient.save()

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, rconf.get("host", "127.0.0.1"), rconf.get("port", 27017), rconf.get("db"), rconf.get("user", None), rconf.get("password", None))
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

    def _datatype_name_to_type(self, name):
        for ev in self.datatype:
            if ev.name == name.upper():
                return ev
        raise ValueError(f"data type({name}) unkown")

    def _trantype_name_to_type(self, name):
        for ev in self.trantype:
            if ev.name == name.upper():
                return ev
        raise ValueError(f"tran type({name}) unkown")

    def stop(self):
        if self._vclient is not None:
            self._vclient.stop()
        self.work_stop()

    def append_tran_type(self, ttype):
        self._tran_types.append(self._trantype_name_to_type(ttype))

    def get_tran_types(self):
        return self._tran_types

    def append_data_type(self, dtype):
        if dtype is None:
            return None
            
        self.__dtypes.append(self._datatype_name_to_type(dtype))

    def get_data_types(self):
        return self.__dtypes

    def set_step(self, step):
        if step is None or step <= 0:
            return
        self._step = step

    def get_step(self):
        return self._step

    def parse_data_type(self, data):
        if data is None or len(data) == 0:
            return self.datatype.UNKOWN

        for etype in self.datatype:
            if etype.name == data.upper():
                return etype

        return self.datatype.UNKOWN

    def is_valid_flag(self, flag):
        return self.parse_tran_type(flag) in self._tran_types
        
    def parse_tran_type(self, flag):
        try:
            if flag is None or len(flag) == 0:
                return self.trantype.UNKOWN

            return self._trantype_name_to_type(flag)
        except Exception as e:
            parse_except(e)
        return self.trantype.UNKOWN

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
            datas = {"flag"         : self.trantype.UNKOWN, 
                    "type"          : self.datatype.UNKOWN, 
                    "from_address"  : None,
                    "to_address"    : None,
                    "nettype"       : None,
                    "state"         : None,
                    "sequence"      : -1,
                    "amount"        : 0,
                    "sender"        : None,
                    "receiver"      : None,
                    "token"         : None,
                    "version"       : 0,
                    "tran_id"       : None,
                    "tran_state"    : False
                    }

            tran = result(error.SUCCEED, datas = datas)
    
            #check transaction state
            datas["version"]    =  transaction.get("version", 0)
            datas["tran_state"] =  transaction.get("success", False)
            if not datas["tran_state"]:
               return tran 

            #must has event(data)
            events = transaction.get("events", None)
            if events is None or len(events) == 0:
               return tran

            data = transaction.get("data")
            if data is None or len(data) == 0:
                return tran

            ret = self.json_to_dict(data)
            if ret.state != error.SUCCEED:
                return tran

            data_dict = ret.datas
            if not self.is_valid_flag(data_dict.get("flag", None)):
                return tran
            
            datas["flag"]           = self.parse_tran_type(data_dict.get("flag", None))
            datas["type"]           = self.parse_data_type(data_dict.get("type", None))
            datas["from_address"]   = data_dict.get("from_address", None)
            datas["to_address"]     = data_dict.get("to_address", None)
            datas["nettype"]        = data_dict.get("nettype", None)
            datas["state"]          = data_dict.get("state", None)
            datas["amount"]         = transaction.get("amount", 0)
            datas["sender"]         = transaction.get("sender", None)
            datas["receiver"]       = transaction.get("receiver", None)
            datas["token"]          = transaction.get("module_address", None)
            tran_id                 = data_dict.get("tran_id", None)
            datas["tran_id"]        = tran_id
            datas["sequence"]   = transaction.get("sequence_number")

            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e, transaction)
        return ret

        
