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
from enum import Enum
from analysis.analysis_base import abase
from analysis.analysis_addresses import addresses
#module name
name="bfilter"

COINS = comm.values.COINS
#load logging
    
class afilter(abase):
    def __init__(self, name = "bfilter", dbconf = None, nodes = None, adbconf = None, pdbconf = None):
        abase.__init__(self, name, dbconf, nodes) #no-use defalut db
        self._addresses = None
        if adbconf is not None:
            self._addresses = addresses(name, adbconf, nodes)

    def __del__(self):
        abase.__del__(self)

    def stop(self):
        abase.stop(self)
        self.work_stop()

    def save_blockinfo(self, blockinfo):
        try:
            coll = self._dbclient.get_collection(self.collection.BLOCKINFO.name.lower(), create = True)
            coll.insert_many([{"_id": blockinfo.get("hash"), "blockinfo":blockinfo}, {"_id":blockinfo.get("height"), "blockhash":blockinfo.get("hash")}])
            ret = result(error.SUCCEED)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_transaction(self, txid, tran, blockhash):
        try:
            coll = self._dbclient.get_collection(self.collection.TRANSACTION.name.lower(), create = True)
            coll.save({"_id":txid, "tran":tran, "blockhash": blockhash})
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_txout(self, txid, txout, blockhash):
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)

            datas = []
            for vout in txout:
                data = {}

                data["_id"] = self.create_txout_id(txid, vout.get("n"))
                #if id is exists, use pre state.  this case is  transaction in the same block ?????
                data["state"] = self.txoutstate.NOUSE.name
                data["vout"] = vout
                data["blockhash"] = blockhash

                ret = coll.find_one({"_id":data["_id"]})
                if ret is not None and len(ret) > 0:
                    state = ret.get("state")
                    data["state"] = state
                    coll.save(data)
                    self._logger.info(f"update txout:{data}")
                    continue
                datas.append(data)

            #may be use save ??????
            if len(datas) > 0:
                coll.insert_many(datas)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def update_txout_state(self, txin, blockhash):
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            for vin in txin:
                coinbase = vin.get("coinbase")
                if coinbase is not None and len(coinbase) > 0:
                    continue

                id = self.create_txout_id(vin.get("txid"), vin.get("vout"))
                coll.update({"_id":id}, {"state":self.txoutstate.USED.name, "blockhash":blockhash}, upsert = True)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def reset_txout_state(self, txin, blockhash):
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            for vin in txin:
                id = self.create_txout_id(vin.get("txid"), vin.get("vout"))
                coll.save(id, {"state":self.txoutstate.NOUSE.name})
            pass
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_address_txout(self, txid, txout, blockhash):
        try:
            if self._addresses is not None:
                ret = self._addresses.save_address_txout(txid, txout, blockhash)
            else:
                ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def start(self):
        i = 0
        #init
        try:
            self._logger.debug("start filter work")
            self._dbclient.use_collection("datainfo", True)
            ret = self._vclient.getblockcount();
            if ret.state != error.SUCCEED:
                return ret
                
            chain_latest_ver = ret.datas - 1


            ret = self._dbclient.get_latest_filter_state()
            assert ret.state == error.SUCCEED, f"get latest filter state failed.txid = {txid}"
            latest_filter_state = self._dbclient.filterstate[ret.datas]

            ret = self._dbclient.get_latest_filter_ver()
            if ret.state != error.SUCCEED:
                return ret
            start_version = self.get_start_version(ret.datas + 1)

            latest_saved_txid = None
            if latest_filter_state == self._dbclient.filterstate.START:
                start_version = start_version - 1

                ret = self._dbclient.get_latest_saved_txid()
                assert ret.state == error.SUCCEED, f"get latest saved txid failed.txid = {txid}"
                latest_saved_txid = ret.datas
            elif latest_filter_state == self._dbclient.filterstate.COMPLETE:
                pass

            #The genesis block coinbase is not considered an ordinary transaction and cannot be retrieved
            if start_version == 0:
                start_version = 1
    
            latest_saved_ver = self._dbclient.get_latest_saved_ver().datas
            
            self._logger.debug(f"latest_saved_ver={latest_saved_ver} start height = {start_version} chain_latest_ver = {chain_latest_ver} ")
            if start_version > chain_latest_ver:
               return result(error.SUCCEED)
            
            version = start_version
            while version < chain_latest_ver:
                if self.work() == False:
                    break

                self._logger.debug(f"get block with height = {version}")
                ret = self._vclient.getblockwithindex(version)
                if ret.state != error.SUCCEED:
                    return ret
                block = ret.datas
                blockhash = block.get("hash")

                ret = self._dbclient.set_latest_filter_ver(version)
                if ret.state != error.SUCCEED:
                    return ret

                if latest_filter_state != self._dbclient.filterstate.START:
                    ret = self.save_blockinfo(block)
                    assert ret.state == error.SUCCEED, f"save block info failed.blockhash = {blockhash}, height={version}"

                txids = block.get("tx")
                if txids is None or len(txids) == 0:
                    version = version + 1
                    latest_saved_txid = None
                    #this block datas is ok
                    ret = self._dbclient.set_latest_filter_state(self._dbclient.filterstate.COMPLETE)
                    if ret.state != error.SUCCEED:
                        return ret
                    continue

                for txid in txids:
                    #some txid is saved, next txid..
                    if latest_saved_txid is not None and txid != latest_saved_txid and len(latest_saved_txid) > 0:
                        continue

                    ret = self._vclient.getrawtransaction(txid = txid)
                    assert ret.state == error.SUCCEED, f"get raw transaction failed.txid = {txid}"
                    tran = ret.datas

                    ret = self.save_transaction(txid, tran, blockhash)
                    assert ret.state == error.SUCCEED, f"save transaction failed.txid = {txid}"

                    ret = self._vclient.gettxoutinfromdata(tran)
                    assert ret.state == error.SUCCEED, f"get transaction vout and vin failed.{txid}"
                    txoutin = ret.datas

                    ret = self.save_txout(txid, ret.datas.get("vout"), blockhash)
                    assert ret.state == error.SUCCEED, f"save txout failed.txid = {txid}"

                    ret = self.update_txout_state(txoutin.get("vin"), blockhash)
                    assert ret.state == error.SUCCEED, f"update txout failed.txid = {txid}"

                    ret = self.save_address_txout(txid, txoutin.get("vout"), blockhash)
                    assert ret.state == error.SUCCEED, f"save address map txout failed.txid = {txid}"

                    ret = self._dbclient.set_latest_saved_txid(txid)
                    #proof

                    ##only restart check
                    latest_saved_txid = None

                ret = self._dbclient.set_latest_filter_state(self._dbclient.filterstate.COMPLETE)
                if ret.state != error.SUCCEED:
                    return ret
                #save to redis db
                self._logger.info(f"save transaction to db. version : {version}")
                version = version + 1
 
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end filter work")
        return ret
        
def works():
    try:
        filter = afilter(name, stmanage.get_db("base"),  stmanage.get_btc_conn(), stmanage.get_db("addresses"))
        ret = filter.start()
        if ret.state != error.SUCCEED:
            print(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
