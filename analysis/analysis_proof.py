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
from db.dbv2b import dbv2b
from vlsopt.violasclient import violasclient, violaswallet, violasserver
from enum import Enum
from db.dbvfilter import dbvfilter
from db.dbvproof import dbvproof
from analysis.analysis_base import abase

#module name
name="aproof"

COINS = comm.values.COINS
class aproof(abase):
    class proofstate(Enum):
        START = 1
        END = 2
        CANCEL = 3
        UNKOWN = 255

    def __init__(self, name = "vproof", ttype = "violas", dtype = "v2b", dbconf = None, fdbconf = None, rdbconf = None, nodes = None, chain = "violas"):
        self._fdbclient = None
        #db use dbvproof, dbvfilter, not use violas/libra nodes
        super().__init__(name, ttype, dtype, None, nodes, chain)
        self._dbclient = None
        self._fdbclient = None
        self._module = None
        if dbconf is not None:
            self._dbclient = dbvproof(name, dbconf.get("host", "127.0.0.1"), dbconf.get("port"), dbconf.get("db"), dbconf.get("password"))
        if fdbconf is not None:
            self._fdbclient = dbvfilter(name, fdbconf.get("host", "127.0.0.1"), fdbconf.get("port"), fdbconf.get("db"), fdbconf.get("password"))

    def __del__(self):
        super().__del__()
        if self._fdbclient is not None:
            self._fdbclient.save()

    def stop(self):
        super().stop()

    def set_module(self, module):
        self._module = module

    def get_module(self):
        return self._module

    def is_valid_moudle(self, module):
        state = self._module == module and module is not None
        print(f"result: {state} {self._module} == {module}")
        return state

    def proofstate_name_to_value(self, name):
        if name is None or len(name) == 0:
            return self.proofstate.UNKOWN

        for estate in self.proofstate:
            if estate.name == name.upper():
                return estate

        return self.proofstate.UNKOWN

    def proofstate_value_to_name(self, value):
        for estate in self.proofstate:
            if estate == value:
                return estate.name.lower()
        return "unkown"

    def is_valid_datatype(self, dtype):
        return dtype in self.get_data_types()

    def check_tran_is_valid(self, tran_info):
        return tran_info.get("flag", None) in self.get_tran_types() and \
               self.proofstate_name_to_value(tran_info.get("state", None)) != self.proofstate.UNKOWN and \
               self.is_valid_datatype(tran_info.get("type")) and \
               self.is_valid_moudle(tran_info.get("token"))

    def is_valid_proofstate_change(self, new_state, old_state):
        if new_state == self.proofstate.UNKOWN:
            return False

        if new_state == self.proofstate.START:
            return True

        if new_state in (self.proofstate.END, self.proofstate.CANCEL) and old_state != self.proofstate.START:
            return False
        return True

    def update_proof_info(self, tran_info):
        try:
            self._logger.debug(f"start update_proof_info tran info: {tran_info}")
            version = tran_info.get("version", None)

            tran_id = None
            new_proof = False
            new_proofstate = self.proofstate_name_to_value(tran_info.get("state", ""))
            if new_proofstate == self.proofstate.START:
                new_proof = True

            self._logger.debug(f"new proof: {new_proof}")
            if new_proof == True:
                ret  = self._dbclient.key_is_exists(version)
                if ret.state != error.SUCCEED:
                    return ret

                #found key = version info, db has old datas , must be flush db?
                if ret.datas == True:
                    return result(error.TRAN_INFO_INVALID, f"key{version} is exists, db datas is old, flushdb ?. violas tran info : {tran_info}")

                #create tran id
                if tran_info["flag"] == self.trantype.BTC.name.lower():
                    tran_id = tran_info["txid"]
                else:
                    tran_id = self.create_tran_id(tran_info["flag"], tran_info["type"], tran_info['sender'], \
                            tran_info['receiver'], tran_info['token'], tran_info['version'])

                tran_info["flag"] = tran_info["flag"].name
                tran_info["type"] = tran_info["type"].name
                tran_info["tran_id"] = tran_id
                ret = self._dbclient.set_proof(version, json.dumps(tran_info))
                if ret.state != error.SUCCEED:
                    return ret
                self._logger.info(f"saved new proof succeed. version = {tran_info.get('version')} tran_id = {tran_id} state={tran_info['state']}")

            else:
                tran_id = tran_info.get("tran_id", None)
                if tran_id is None or len(tran_id) == 0:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran info : {tran_info}")

                #get tran info from db(tran_id -> version -> tran info)

                ret = self._dbclient.get_proof_by_hash(tran_id)
                if ret.state != error.SUCCEED:
                    #btc transaction is end , diff libra and violas
                    if tran_info["flag"] == self.trantype.BTC:
                        tran_info["flag"] = tran_info["flag"].name
                        tran_info["type"] = tran_info["type"].name
                        ret = self._dbclient.set_proof(version, json.dumps(tran_info))
                        if ret.state != error.SUCCEED:
                            return ret
                        return result(error.SUCCEED, "", {"new_proof":new_proof, "tran_id":tran_id})

                    self._logger.debug(f"get_proof_by_hash({tran_id}) failed.")
                    return ret

                if ret.datas is None or len(ret.datas) == 0:
                    return result(error.TRAN_INFO_INVALID, 
                            f"tran_id {tran_id} not found value or key is not found.tran version : {tran_info.get('version')}")

                db_tran_info = json.loads(ret.datas)

                db_tran_id = db_tran_info.get("tran_id", None)
                if db_tran_id is None or len(db_tran_id) == 0 or db_tran_id != tran_id:
                    return result(error.TRAN_INFO_INVALID, f"new tran data info is invalid, tran version : {tran_info.get('version')}")

                old_proofstate = self.proofstate_name_to_value(db_tran_info.get("state", ""))
                if not self.is_valid_proofstate_change(new_proofstate, old_proofstate):
                    return result(error.TRAN_INFO_INVALID, f"change state to {new_proofstate.name} is invalid. \
                            old state is {old_proofstate.name}. tran version: {tran_info.get('version')}")

                #only recevier can change state (start -> end/cancel)
                if db_tran_info.get("receiver", "start state receiver") != tran_info.get("sender", "to end address"):
                    return result(error.TRAN_INFO_INVALID, f"change state error. sender[state = end] != recever[state = start] \
                            sender: {tran_info.get('receiver')}  receiver : {db_tran_info.get('sender')} version = {tran_info.get('version')}") 

                db_tran_info["state"] = tran_info["state"]
                self._dbclient.set_proof(db_tran_info.get("version"), json.dumps(db_tran_info))
                self._logger.info(f"change state succeed. version = {db_tran_info.get('version')} tran_id = {db_tran_id} state={db_tran_info['state']}")

            ret = result(error.SUCCEED, "", {"new_proof":new_proof, "tran_id":tran_id})
        except Exception as e:
            ret = parse_except(e)
        return ret
        
    def update_min_version_for_start(self):
        try:
            self._logger.debug(f"start update_min_version_for_start")
            #update min version for state is start
            ret = self._dbclient.get_proof_min_version_for_start()
            if ret.state != error.SUCCEED:
                return ret
            start_version = max(int(ret.datas), self.get_min_valid_version())

            ret = self._dbclient.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            max_version = ret.datas

            keys = self._dbclient.list_version_keys(start_version)
            new_version = start_version
            for version in keys:
                if self.work() != True:
                    break
                    
                #self._logger.debug(f"check version {version}")

                ret = self._dbclient.get(version)
                if ret.state != error.SUCCEED:
                    return ret

                if ret.datas is None:
                    continue

                new_version = version
                tran_data = json.loads(ret.datas)
                if self.proofstate_name_to_value(tran_data.get("state")) == self.proofstate.START and \
                        self.is_valid_moudle(tran_data.get("token")):
                    break

            ret = self._dbclient.set_proof_min_version_for_start(new_version)
            if ret.state == error.SUCCEED and start_version != new_version:
                self._logger.info(f"update min version for start(proof state) {start_version} -> {version}")
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
            ret = self._fdbclient.get_latest_saved_ver()
            if ret.state != error.SUCCEED:
                return ret
            latest_saved_ver = ret.datas
            max_version = latest_saved_ver

            #not found new transaction to change state
            if start_version > max_version:
                self._logger.debug(f"start version:{start_version} max version:{max_version}")
                return result(error.SUCCEED)

            version  = start_version
            count = 0
            self._logger.debug(f"proof latest_saved_ver={self._dbclient.get_latest_saved_ver().datas} start version = {start_version}  \
                    step = {self.get_step()} valid transaction latest_saved_ver = {latest_saved_ver} ")

            keys = self._fdbclient.list_version_keys(start_version)
            latest_filter_ver = start_version
            for version in keys:
                try:
                    if count >= self.get_step() and self.work() == False:
                        break
                    #record last version(parse), maybe version is not exists
                    #self._logger.debug(f"parse transaction:{version}")

                    latest_filter_ver = version

                    ret = self._fdbclient.get(version)
                    if ret.state != error.SUCCEED:
                        return ret

                    if ret.datas is None:
                        continue

                    tran_data = json.loads(ret.datas)
                    ret = self.parse_tran(tran_data)
                    if ret.state != error.SUCCEED: 
                        continue

                    tran_filter = ret.datas
                    if self.check_tran_is_valid(tran_filter) != True:
                        continue

                    self._logger.debug(f"transaction parse: {tran_filter}")

                    #this is target transaction, todo work here
                    ret = self.update_proof_info(tran_filter)
                    if ret.state != error.SUCCEED:
                        self._logger.error(ret.message)
                        continue

                    #mark it, watch only, True: new False: update
                    # maybe btc not save when state == end, because start - > end some minue time
                    if ret.datas.get("new_proof") == True or tran_filter.get("flag") == self.trantype.BTC:  
                        self._dbclient.set_latest_saved_ver(version)

                    tran_id = ret.datas.get("tran_id")
                    ret = self._dbclient.get_proof_by_hash(tran_id)
                    if ret.state != error.SUCCEED:
                        return ret
                    
                    if (ret.datas is not None or len(ret.datas) > 0) and self.can_record():
                        ret = self._rdbclient.update_address_info(json.loads(ret.datas))
                        if ret.state != error.SUCCEED:
                            return ret
                    count += 1
                except Exception as e:
                    ret = parse_except(e)
                finally:
                    #version += 1
                    pass

            #here version is not analysis
            self._dbclient.set_latest_filter_ver(latest_filter_ver)
            self.update_min_version_for_start()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end vproof work")

        return ret

def works(ttype, dtype, basedata):
    try:
        #ttype: chain name. data's flag(violas/libra). ex. ttype = "violas"
        #dtype: save transaction's data type(v2b v2l l2v) . ex. dtype = "v2b" 
        #basedata: transaction info(vfilter/lfilter), vfilter: filter transaction from violas chain; \
        #        lfilter: filter transaction from violas chain. ex. basedata = "vfilter" 
        #load logging
        logger = log.logger.getLogger(name) 

        _vproof = vproof(name, ttype, dtype, stmanage.get_db(dtype), stmanage.get_db(basedata), stmanage.get_violas_nodes())
        _vproof.set_step(stmanage.get_db(dtype).get("step", 100))
        ret = _vproof.start()
        if ret.state != error.SUCCEED:
            logger.error(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret
