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
from vrequest.request_base import requestbase

#module name
name="requestfilter"

#load logging

class requestfilter(requestbase):
    def __init__(self, name, dbconf):
        requestbase.__init__(self, name, dbconf)

    def __del__(self):
        pass

    
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
    client = requestfilter(name, stmanage.get_db("base"))
    ret = client.list_opreturn_txids(0, 10)
    
    print("*************************** state = end *********************************")
    for data in ret.datas:
        json_print(data)

if __name__ == "__main__":
    works()
