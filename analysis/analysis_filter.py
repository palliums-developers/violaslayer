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
from db.dbv2b import dbv2b
from enum import Enum
from db.dbvfilter import dbvfilter
from analysis.analysis_base import abase
#module name
name="bfilter"

COINS = comm.values.COINS
#load logging
    
class afilter(abase):
    def __init__(self, name = "bfilter", dbconf = None, nodes = None):
        #db user dbvfilter
        abase.__init__(self, name, dbconf, nodes) #no-use defalut db

    def __del__(self):
        abase.__del__(self)

    def stop(self):
        abase.stop(self)
        self.work_stop()

    def save_blockinfo(self, blockinfo):
        try:
            coll = self._dbclient.get_collection(self.collection.BLOCKINFO.name.lower(), create = True)
            coll.insert_many([{"_id": blockinfo.get("txid"), "blockinfo":blockinfo}, {"_id":blockinfo.get("height"), "blockhash":blockinfo.get("hash")}])
            ret = result(error.SUCCEED)
        except Exception as e:
            parse_except(e)
        return ret

    def save_transaction(self, txid, tran):
        try:
            coll = self._dbclient.get_collection(self.collection.TRANSACTION.name.lower(), create = True)
            coll.save_with_id(txid, tran)
            ret = result(error.SUCCEED)
        except Exception as e:
            parse_except(e)
        return ret

    def create_txout_id(self, txid, n):
        return f"{txid}_{n}"

    def save_txout(self, txid, txout)
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)

            datas = []
            for vout in txout:
                data = {}
                ret = self._client.parsevout(vout)
                if ret.state != error.SUCCEED:
                    return ret

                data["_id"] = self.create_txout_id(txid, ret.get("n"))
                #if id is exists, use pre state.  this case is  transaction in the same block ?????
                data["state"] = self.txoutstate.NOUSE.name
                data["vout"] = vout

                ret = coll.find_one({"_id":data["_id"]})
                if ret.state != error.SUCCEED:
                    return ret
                if ret.datas is not None or len(ret.datas) > 0:
                    state = ret.datas.get("state")
                    data["state"] = state
                    coll.save(data["_id"], data)
                    self._logger.info(f"update txout:{data}")
                    continue
                datas.append(data)

            #may be use save ??????
            if len(datas) > 0:
                coll.insert_many(datas)

            ret = result(error.SUCCEED)
        except Exception as e:
            parse_except(e)
        return ret
    def update_txout_state(self, txin)
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            for vin in txin:
                id = create_txout_id(vin.get("txid"), vin.get("vout"))
                coll.save(id, {"state":self.txoutstate.USED.name})
            pass
        except Exception as e:
            parse_except(e)
        return ret

    def save_address_txout(self, txout)
        try:
            pass
        except Exception as e:
            parse_except(e)
        return ret

    def start(self):
        i = 0
        #init
        try:
            self._logger.debug("start filter work")
            ret = self._vclient.getblockcount();
            if ret.state != error.SUCCEED:
                return ret
                
            chain_latest_ver = ret.datas - 1

            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            start_version = self.get_start_version(ret.datas + 1)
    
            latest_saved_ver = self._dbclient.get_latest_saved_ver().datas
            
            self._logger.debug(f"latest_saved_ver={latest_saved_ver} start version = {start_version}  step = {self.get_step()} chain_latest_ver = {chain_latest_ver} ")
            if start_version > chain_latest_ver:
               return result(error.SUCCEED)
    

            version = start_version
            while True:
                if self.work() == False:
                    break

                ret = self._vclient.getblockwithindex(start_version)
                if ret.state != error.SUCCEED:
                    return ret
                block = ret.datas

                ret = self._dbclient.set_latest_filter_ver(version)
                if ret.state != error.SUCCEED:
                    return ret


                tran_data = self.get_tran_data(data)   

                if self.is_target_tran(tran_data) == False:
                    continue

                #save to redis db
                ret = self._dbclient.set(version, json.dumps(tran_data))
                if ret.state != error.SUCCEED:
                    return ret
                self._dbclient.set_latest_saved_ver(version)
                self._logger.info(f"save transaction to db. version : {version}")
 
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end filter work")
        return ret
        
def works(ttype, dtype):
    try:
        #ttype: chain name. data's flag(violas/libra). ex. ttype = "violas"
        #dtype: save transaction's data type(vfilter/lfilter) . ex. dtype = "vfilter" 
        filter = vfilter(name, ttype, None, stmanage.get_db(dtype),  stmanage.get_violas_nodes())
        filter.set_step(stmanage.get_db(dtype).get("step", 1000))
        ret = filter.start()
        if ret.state != error.SUCCEED:
            print(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
