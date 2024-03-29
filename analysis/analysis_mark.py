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
class amarkproof(aproofbase):

    def __init__(self, name = "amarkproof", dbconf = None, fdbconf = None, nodes = None, chain = "btc"):
        super().__init__(name, dbconf, fdbconf, nodes, chain)

    def __del__(self):
        super().__del__()

    def stop(self):
        super().stop()

    def save_proof_info(self, tran_info):
        pass
        try:
            self._logger.debug(f"start save_proof_info tran info: {tran_info}")

            tran_id = None
            proofstate = tran_info.get("state", "")
            self._dbclient.use_collection_datas()
            tran_id = self.create_tran_id(tran_info["address"], tran_info["sequence"])
            if proofstate in (payload.txtype.EX_MARK, payload.txtype.BTC_MARK):
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

            ret = result(error.SUCCEED, "", {"tran_id":tran_id})
        except Exception as e:
            ret = parse_except(e)
        return ret

    def start(self):
        try:
            self._logger.debug("start markproof work")

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
                        self._logger.warning(f"transaction({txid}) is invalid. {tran_filter.get('state')} is not target type:{self.valid_txtype}")
                        continue

                    self._logger.debug(f"transaction parse: {tran_filter}")

                    #this is target transaction, todo work here
                    tran_filter["index"] = version
                    tran_filter["version"] = version
                    ret = self.save_proof_info(tran_filter)
                    if ret.state != error.SUCCEED:
                        self._logger.error(ret.message)
                        continue

                    #mark it, watch only, True: new False: update
                    # maybe btc not save when state == end, because start - > end some minue time
                    self._dbclient.set_latest_saved_ver(version)
                    
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
        dtype = "markproof"
        obj = amarkproof(name="markproof", \
                dbconf=stmanage.get_db(dtype), \
                fdbconf=stmanage.get_db(basedata), \
                nodes = stmanage.get_btc_conn() \
                )
        obj.append_valid_txtype(payload.txtype.BTC_MARK)
        obj.append_valid_txtype(payload.txtype.EX_MARK)
        obj.set_step(1)
        ret = obj.start()

        if ret.state != error.SUCCEED:
            logger.error(ret.message)
    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
