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
from db.dbvproof import dbvproof
from baseobject import baseobject
from enum import Enum
from vrequest.request_base import requestbase 
from analysis.analysis_proof import aproof
from btc.payload import payload

#module name
name="requestproof"

#load logging

class requestproof(requestbase):
    proofstate = payload.txstate
    prooftype = payload.txtype

    def __init__(self, name, dbconf):
        requestbase.__init__(self, name, dbconf)

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvproof(name, \
                    rconf.get("host", "127.0.0.1:37017"), \
                    rconf.get("db"), rconf.get("user"), \
                    rconf.get("password"), \
                    rconf.get("authdb", "admin"), \
                    newdb = False, \
                    rsname=rconf.get("rsname"))
            self._dbclient.use_collection_datas()
        return self._dbclient

    def __del__(self):
        pass
    
    def list_exproof(self, receiver = None, opttype = None, state = None, start = 0, limit = 10):
        try:
            self._dbclient.use_collection_datas()
            filters = [{"_id":{"$type":"int"}}, {"_id":{"$gte":start}}]
            if opttype is not None:
                filters.append({"type":opttype})

            if receiver is not None:
                filters.append({"receiver":receiver})

            if state is not None:
                filters.append({"state":state.lower()})

            ret = self._dbclient.find({"$and": filters}, limit = limit)
            if ret.state != error.SUCCEED:
                return ret

            datas = ret.datas.sort("_id", pymongo.ASCENDING)
            ret = result(error.SUCCEED, "", [data for data in datas])
        except Exception as e:
            ret = parse_except(e)
        return ret


    def list_proof_btcmark(self, receiver, start = 0, limit = 10):
        return self.list_exproof(receiver, self.prooftype.BTCMARK.name.lower(),\
                    self.proofstate.BTCMARK.name.lower(), start, limit)

    def list_proof_mark(self, receiver, start = 0, limit = 10):
        return self.list_exproof(receiver, self.prooftype.V2BMARK.name.lower(),\
                    self.proofstate.MARK.name.lower(), start, limit)

    def check_proof_is_target_state(self, address, sequence, txstate):
        try:
            tran_id = aproof.create_tran_id(address, sequence)
            ret = self._dbclient.get_proof(tran_id)
            if ret.state != error.SUCCEED:
                #btc transaction is end , diff libra and violas
                return ret

            db_tran_info = ret.datas
            state = payload.state_name_to_value(db_tran_info.get("state"))
            txstate = payload.state_name_to_value(txstate)

            datas = {"result": str(state == txstate).lower()}
            
            ret = result(error.SUCCEED, "", datas)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_transaction(self, tran_id):
        try:
            ret = self._dbclient.get_proof(tran_id)
            if ret.state != error.SUCCEED:
                return ret

        except Exception as e:
            ret = parse_except(e)
        return ret
def works():
    client = requestproof(name, stmanage.get_db("proof"))
    ret = client.list_exproof(receiver, "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB", state = requestproof.proofstate.END.name)
    
    print("*************************** state = end *********************************")
    for data in ret.datas:
        json_print(data)

    ret = client.list_exproof(receiver = "2N2YasTUdLbXsafHHmyoKUYcRRicRPgUyNB", state = requestproof.proofstate.START.name)
    print("*************************** state = start *********************************")
    for data in ret.datas:
        json_print(data)
if __name__ == "__main__":
    works()
