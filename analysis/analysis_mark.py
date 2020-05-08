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
name="aproof"

COINS = comm.values.COINS
class amark(abase):

    def __init__(self, name = "amark", dbconf = None, fdbconf = None, nodes = None, chain = "btc"):
        self._fdbclient = None
        #db use dbvproof, dbvfilter, not use violas/libra nodes
        super().__init__(name, None, nodes)
        self._dbclient = None
        self._fdbclient = None
        self._module = None
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
        proofstate = tran_info.get("state", "")
        return self.is_valid_proofstate(proofstate) and tran_info.get("valid")

    def get_opreturn_txids(self, index, limit = 10, sort = pymongo.ASCENDING):
        self._logger.debug("get_opreturn_txids(index={index})")
        coll = self._fdbclient.get_collection(self.collection.OPTRANSACTION.name.lower(), create = True)
        datas = coll.find({"_id":{"$gte":index}}, limit = limit)#.sort(["_id", sort])
        print(datas)
        return datas

    def is_valid_proofstate(self, state):
        assert isinstance(state, payload.txtype), "state type is invalid."
        if state == payload.txtype.UNKNOWN:
            return False

        if state not in (payload.txtype.EX_START, payload.txtype.EX_END, payload.txtype.EX_CANCEL):
            return False

        return True

    def is_valid_proofstate_change(self, new_state, old_state):
        if new_state == payload.txtype.UNKNOWN:
            return False

        if new_state == payload.txtype.EX_START:
            return True

        if new_state in (payload.txtype.EX_END, payload.txtype.EX_CANCEL) and old_state != payload.txtype.EX_START:
            return False
        return True

    def proofstate_name_to_value(self, name):
        return payload.state_name_to_value(name)

    def proofstate_value_to_name(self, value):
        return payload.state_value_to_name(value)

    def save_proof_info(tran_info):
        pass

    def start(self):
        try:
            self._logger.debug("start vproof work")

            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret

            start_version = self.get_start_version(ret.datas + 1)

            #can get max version 
            ret = self._fdbclient.get_latest_opreturn_index()
            if ret.state != error.SUCCEED:
                return ret
            latest_saved_ver = ret.datas
            max_version = latest_saved_ver

            #not found new transaction to change state
            if start_version > max_version:
                self._logger.debug(f"start version:{start_version} max version({self._fdbclient.db_pos}):{max_version}")
                return result(error.SUCCEED)

            version  = start_version
            count = 0
            self._logger.debug(f"proof latest_saved_ver={self._dbclient.get_latest_saved_ver().datas} start version = {start_version}  \
                    step = {self.get_step()} valid transaction latest_saved_ver = {latest_saved_ver} ")

            datas = self.get_opreturn_txids(version, limit = self.get_step())
            latest_filter_ver = start_version
            for data in datas:
                try:
                    version = data.get("_id")
                    txid = data.get("txid")
                    if self.work() == False:
                        break
                    #record last version(parse), maybe version is not exists
                    self._logger.debug(f"parse transaction:txid = {txid} index={version}")

                    latest_filter_ver = version

                    print(txid)
                    ret = self.get_transaction(txid)
                    if ret.state != error.SUCCEED:
                        self._logger.error(ret.message)
                        return ret

                    tran_data = ret.datas
                    ret = self.parse_tran(tran_data)
                    if ret.state != error.SUCCEED: 
                        self._logger.error(ret.to_json())
                        continue

                    tran_filter = ret.datas
                    if self.check_tran_is_valid(tran_filter) != True:
                        self._logger.warning(f"transaction({txid}) is invalid.")
                        continue

                    self._logger.debug(f"transaction parse: {tran_filter}")

                    #this is target transaction, todo work here
                    tran_filter["index"] = version
                    ret = self.save_proof_info(tran_filter)
                    if ret.state != error.SUCCEED:
                        self._logger.error(ret.message)
                        continue

                    #mark it, watch only, True: new False: update
                    # maybe btc not save when state == end, because start - > end some minue time
                    if ret.datas.get("new_proof") == True:  
                        self._dbclient.set_latest_saved_ver(version)
                    
                    count += 1
                except Exception as e:
                    ret = parse_except(e)
                finally:
                    pass

            #here version is not analysis
            self._dbclient.set_latest_filter_ver(latest_filter_ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end vproof work")

        return ret

def works():
    try:
        #load logging
        logger = log.logger.getLogger(name) 

        basedata = "base"
        dtype = "b2vproof"
        obj = aproof(name="b2vproof", \
                dbconf=stmanage.get_db(dtype), \
                fdbconf=stmanage.get_db(basedata), \
                nodes = stmanage.get_btc_conn() \
                )
        obj.set_step(stmanage.get_db(dtype).get("step", 100))
        ret = obj.start()

        if ret.state != error.SUCCEED:
            logger.error(ret.message)
    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
