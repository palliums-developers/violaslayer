#!/usr/bin/python3
'''
btc exchange request
'''
import operator
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import traceback
import datetime
import pymongo
import stmanage
import random
import redis
import json
from comm.error import error
from comm.result import result, parse_except
from comm.functions import json_print
from db.dbvbase import dbvbase
from baseobject import baseobject
from enum import Enum

#module name
name="requestfilter"

#load logging

class requestfilter(baseobject):
    def __init__(self, name, dbconf):
        baseobject.__init__(self, name)
        self._dbclient = None
        self._connect_db(name, dbconf)

    def __del__(self):
        pass

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvbase(name, \
                    rconf.get("host", "127.0.0.1:37017"), \
                    rconf.get("db"), rconf.get("user"), \
                    rconf.get("password"), \
                    rconf.get("authdb", "admin"), \
                    newdb = False, \
                    rsname=rconf.get("rsname"))
        return self._dbclient
    
    def list_opreturn_txids(self, start = 0, limit = 10):
        try:
            self._dbclient.use_collection("optransaction")
            ret = self._dbclient.find({"$and": [{"_id":{"$type":"int"}}, {"_id":{"$gte":start}}]}, limit = limit)
            if ret.state != error.SUCCEED:
                return ret

            datas = ret.datas.sort("_id", pymongo.ASCENDING)
            ret = result(error.SUCCEED, "", [data for data in datas])
        except Exception as e:
            ret = parse_except(e)
        return ret
def works():
    client = requestproof(name, stmanage.get_db("b2vproof"))
    ret = client.list_exproof_end("2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB")
    
    print("*************************** state = end *********************************")
    for data in ret.datas:
        json_print(data)

    ret = client.list_exproof_start("2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB")
    print("*************************** state = start *********************************")
    for data in ret.datas:
        json_print(data)
if __name__ == "__main__":
    works()
