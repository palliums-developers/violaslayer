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
from analysis.analysis_proof_base import aproofbase
from btc.payload import payload
from btc.btcclient import btcclient

#module name
name="aproof"

COINS = comm.values.COINS
class aproof(aproofbase):

    def __init__(self, name = "vproof", dbconf = None, fdbconf = None, nodes = None, chain = "btc"):
        super().__init__(name, dbconf, fdbconf, nodes, chain)

    def __del__(self):
        super().__del__()

    def stop(self):
        super().stop()

    def is_valid_proofstate_change(self, new_state, old_state):
        if new_state == payload.txtype.UNKNOWN:
            return False

        if new_state == payload.txtype.EX_START:
            return True

        if new_state in (payload.txtype.EX_END, payload.txtype.EX_CANCEL) and old_state != payload.txtype.EX_START:
            return False
        return True

    def update_proof_info(self, tran_info):
        try:
            self._logger.debug(f"start update_proof_info tran info: {tran_info}")

            tran_id = None
            new_proof = False
            new_proofstate = tran_info.get("state", "")
            if new_proofstate == payload.txtype.EX_START:
                new_proof = True

            self._dbclient.use_collection_datas()
            self._logger.debug(f"new proof: {new_proof}")
            tran_id = self.create_tran_id(tran_info["address"], tran_info["sequence"])
            if new_proof == True:
                ret  = self._dbclient.key_is_exists({"_id": tran_id})
                if ret.state != error.SUCCEED:
                    return ret

                #found key = index info, db has old datas , must be flush db?
                if ret.datas == True:
                    return result(error.TRAN_INFO_INVALID, f"key{tran_id} is exists, db datas is old, flushdb ?. violas tran info : {tran_info}")

                #create tran id

                tran_info["tran_id"] = tran_id
                tran_info["state"] = self.proofstate_value_to_name(tran_info["state"])
                ret = self._dbclient.set_proof(tran_id, tran_info)
                if ret.state != error.SUCCEED:
                    return ret
                self._logger.info(f"saved new proof succeed. index = {tran_info.get('index')} tran_id = {tran_id} state={tran_info['state']}")

            else:
                if tran_id is None or len(tran_id) == 0:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran info : {tran_info}")

                #get tran info from db(tran_id -> index -> tran info)

                ret = self._dbclient.get_proof(tran_id)
                if ret.state != error.SUCCEED:
                    #btc transaction is end , diff libra and violas
                    self._logger.debug(f"find transaction ({tran_id}) failed.")
                    return ret

                if ret.datas is None or len(ret.datas) == 0:
                    return result(error.TRAN_INFO_INVALID, 
                            f"tran_id {tran_id} not found value or key is not found.tran txid : {tran_info.get('txid')}")

                db_tran_info = ret.datas

                db_tran_id = db_tran_info.get("tran_id")
                if db_tran_id is None or len(db_tran_id) == 0 or db_tran_id != tran_id:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran id : {db_tran_id}")

                old_proofstate = self.proofstate_name_to_value(db_tran_info.get("state", ""))
                if not self.is_valid_proofstate_change(new_proofstate, old_proofstate):
                    return result(error.TRAN_INFO_INVALID, f"change state to {new_proofstate.name} is invalid. \
                            old state is {old_proofstate.name}. tran id: {tran_id}")

                #only recevier can change state (start -> end/cancel)
                if db_tran_info.get("receiver", "start state receiver") != tran_info.get("issuser", "to end address"):
                    return result(error.TRAN_INFO_INVALID, f"change state error. issuser[state = end] != recever[state = start] \
                            issuser: {tran_info.get('receiver')}  receiver : {db_tran_info.get('issuser')} tran_id = {tran_id}") 

                
                db_tran_info["state"] = self.proofstate_value_to_name(tran_info["state"])
                db_tran_info["vheight"] = tran_info["vheight"]
                db_tran_info["update_txid"] = tran_info["update_txid"]
                db_tran_info["update_block"] = tran_info["update_block"]
                self._dbclient.update_proof(tran_id, db_tran_info)
                self._logger.info(f"change state succeed. tran_id = {db_tran_id} state={db_tran_info['state']}")

            ret = result(error.SUCCEED, "", {"new_proof":new_proof, "tran_id":tran_id})
        except Exception as e:
            ret = parse_except(e)
        return ret

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
                    ret = self.update_proof_info(tran_filter)
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
