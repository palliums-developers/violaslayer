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
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from db.dbvproof import dbvproof
from baseobject import baseobject

#module name
name="record"

class record(baseobject):
    def __init__(self, name, rdbconf):
        baseobject.__init__(self, name)
        #db use dbvproof, dbvfilter, not use violas/libra nodes
        self._rdbclient = None
        if rdbconf is not None:
            self._rdbclient= dbvproof(name, rdbconf.get("host", "127.0.0.1"), rdbconf.get("port"), rdbconf.get("db"), rdbconf.get("password"))

    def __del__(self):
        if self._rdbclient is not None:
            self._rdbclient.save()

    def can_record(self):
        return self._rdbclient is not None

    def update_address_info(self, tran_info):
        try:
            if self._rdbclient is None:
                return result(error.SUCCEED, "db not set")

            self._logger.debug(f"start update_address_info:{tran_info['version']}, state:{tran_info['state']}")
            version = tran_info.get("version", None)

            name = self._rdbclient.create_haddress_name(tran_info)
            key = self._rdbclient.create_haddress_key(tran_info)
            ret = self._rdbclient.hexists(name, key)
            if ret.state != error.SUCCEED:
                self._logger.error(f"check state info <name={name}> failed, check db is run. messge:{ret.message}")
                return ret

            if ret.datas == 1:
                info = self._rdbclient.hget(name, key)
                if info.state != error.SUCCEED or info.datas is None:
                    self._logger.error(f"get state info <name={name}, key={key}> failed, check db is run. messge:{info.message}")
                    return info
                data = json.loads(info.datas)
                data["state"] = tran_info["state"]
                ret = self._rdbclient.hset(name, key, json.dumps(data))
                if ret.state != error.SUCCEED:
                    self._logger.error(f"update state info <name={name}, key={key}, data={json.dumps(data)}> failed, check db is run. messge:{ret.message}")
                    return ret
            else:
                data = self._rdbclient.create_haddress_value(tran_info)
                ret = self._rdbclient.hset(name, key, data)
                if ret.state != error.SUCCEED:
                    self._logger.error(f"set state info <name={name}, key={key}, data={data}> failed, check db is run. messge:{ret.message}")
                    return ret

        except Exception as e:
            ret = parse_except(e)
        return ret




