#!/usr/bin/python3
import operator
import signal
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
from btc.payload import payload
from db.dbvfilter import dbvfilter
#module name
name="bfilter"

COINS = comm.values.COINS
#load logging
    
class afilter(abase):
    def __init__(self, name = "bfilter", dbconf = None, nodes = None, **argkeys):
        abase.__init__(self, name, None, nodes) #no-use defalut db
        self.__maptolocal = argkeys.get("maptolocal", False)
        self.__storeoptran = argkeys.get("storeoptran", True)
        self._connect_db(name, dbconf)

    def _connect_db(self, name, rconf):
        self._dbclient = None
        if rconf is not None:
            self._dbclient = dbvfilter(name, rconf.get("host", "127.0.0.1:37017"), rconf.get("db"), 
                    rconf.get("user", None), rconf.get("password", None), rconf.get("authdb", "admin"), 
                    newdb = rconf.get("newdb", True), rsname=rconf.get("rsname", None))
        return self._dbclient

    def __del__(self):
        abase.__del__(self)

    @property
    def map_to_local(self):
        return self.__maptolocal

    @property
    def store_op_tran(self):
        return self.__storeoptran

    def stop(self):
        abase.stop(self)
        self.work_stop()

    def save_blockinfo(self, blockinfo):
        try:
            self._logger.debug("save_blockinfo({blockinfo.get('hash')})")
            coll = self._dbclient.get_collection(self.collection.BLOCKINFO.name.lower(), create = True)
            coll.insert_many([{"_id": blockinfo.get("hash"), "blockinfo":blockinfo}, {"_id":blockinfo.get("height"), "blockhash":blockinfo.get("hash")}])
            ret = result(error.SUCCEED)

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_transaction(self, txid, tran, blockhash, session=None):
        try:
            self._logger.debug("save_transaction(txid={txid}, session={session})")
            coll = self._dbclient.get_collection(self.collection.TRANSACTION.name.lower(), create = True)
            coll.insert_one({"_id":txid, "tran":tran, "blockhash": blockhash}, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_txout(self, txid, txout, blockhash, session=None):
        try:
            self._logger.debug("save_txout(txid={txid}, blockhash={blockhash} session={session})")
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)

            datas = []
            for vout in txout:
                data = {}
                data["_id"] = self.create_txout_id(txid, vout.get("n"))
                #if id is exists, use pre state.  this case is  transaction in the same block ?????
                data["state"] = self.txoutstate.NOUSE.name
                data["vout"] = vout
                data["txid"] = txid
                data["blockhash"] = blockhash

                print(data["_id"])
                ret = coll.find_one({"_id":data["_id"]})
                if ret is not None and len(ret) > 0:
                    state = ret.get("state")
                    data["state"] = state
                    coll.update_one({"_id":data["_id"]}, {"$set":data}, session=session)
                    self._logger.info(f"update txout:{data}")
                    continue
                datas.append(data)
                coll.insert_one(data, session=session)

            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def create_txout_index(self):
        try:
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            coll.createindex([("_id", pymongo.ASCENDING)], background=True, name="idx_txout_id")
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_txout_state(self, txin, blockhash, session=None):
        try:
            self._logger.debug("update_txout_state(blockhash={blockhash} session={session})")
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            for vin in txin:
                coinbase = vin.get("coinbase")
                if coinbase is not None and len(coinbase) > 0:
                    continue

                id = self.create_txout_id(vin.get("txid"), vin.get("vout"))
                coll.update_one({"_id":id}, {"$set":{"state":self.txoutstate.USED.name, "blockhash":blockhash}}, upsert = True, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def reset_txout_state(self, txin, blockhash, session=None):
        try:
            self._logger.debug("reset_txout_state(blockhash={blockhash} session={session})")
            coll = self._dbclient.get_collection(self.collection.TXOUT.name.lower(), create = True)
            for vin in txin:
                id = self.create_txout_id(vin.get("txid"), vin.get("vout"))
                coll.update_one({"_id":id}, {"$set":{"state":self.txoutstate.NOUSE.name}}, upsert= True, session=session)
            pass
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_opreturn(self, txout):
        try:
            find = False
            for i, value in enumerate(txout):
                script_pub_key = txout[i]["scriptPubKey"]
                if script_pub_key.get("type", "") == "nulltype":
                    find = True
                    break
            ret = result(error.SUCCEED, "", find)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_opreturn(self, txout):
        try:
            opstr = None
            for i, value in enumerate(txout):
                script_pub_key = txout[i]["scriptPubKey"]
                if script_pub_key.get("type", "") == "nulltype":
                    opstr = script_pub_key.get("hex")
                    break
            ret = result(error.SUCCEED, "", opstr)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save_opreturn_txid(self, index, txid, session=None):
        try:
            self._logger.debug("save_opreturn_txid(index={index}, txid={txid} session={session})")
            coll = self._dbclient.get_collection(self.collection.OPTRANSACTION.name.lower(), create = True)
            coll.insert_one({"_id":index, "txid":txid}, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def init_collections(self):
        try:
            colls =  self._dbclient.list_collection_names().datas
            for collname in self.collection:
                if collname.name.lower() in colls:
                    continue
                self._logger.debug(f"create collection:{collname.name.lower()}")
                coll = self._dbclient.get_collection(collname.name.lower(), create = True)
                coll.update_one({"_id":"collname"}, {"$set":{"name":collname.name.lower()}}, upsert=True)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def start(self):
        i = 0
        #init
        try:
            self._logger.debug(f"start filter work(map_to_local:{self.map_to_local}, store_op_tran:{self.store_op_tran})")
            payload_parse = payload(name)
            self.init_collections()
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

            #opreturn transaction index -> txid
            ret = self._dbclient.get_latest_opreturn_index()
            if ret.state != error.SUCCEED:
                return ret
            latest_opreturn_index = ret.datas + 1

            latest_saved_txid = None

            #pre not complete block txix, continue process it
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
            
            if start_version > chain_latest_ver:
               return result(error.SUCCEED)
            
            version = start_version
            self._logger.debug(f"height = {start_version} max height = {chain_latest_ver} ")
            self._logger.debug(f"latest filter state = {latest_filter_state.name}, latest saved txid = {latest_saved_txid}")

            step = self.get_step()
            if step > 0 and chain_latest_ver > version + step:
                chain_latest_ver = version + step

            while version < chain_latest_ver:
                if self.work() == False:
                    self._logger.debug(f"recver stop command, next height: {version}")
                    return result(error.WORK_STOP)

                self._logger.debug(f"get block with height = {version}")
                ret = self._vclient.getblockwithindex(version)
                if ret.state != error.SUCCEED:
                    return ret
                block = ret.datas
                blockhash = block.get("hash")

                if latest_filter_state != self._dbclient.filterstate.START:
                    ret = self._dbclient.set_latest_filter_ver(version)
                    assert ret.state == error.SUCCEED, \
                        f"set latest filter height failed.blockhash = {blockhash}, height={version}"

                    if self.map_to_local:
                        ret = self.save_blockinfo(block)
                        assert ret.state == error.SUCCEED, \
                                f"save block info failed.blockhash = {blockhash}, height={version}"

                txids = block.get("tx")
                #empty block
                if txids is None or len(txids) == 0:
                    version = version + 1
                    latest_saved_txid = None
                    #this block datas is ok
                    ret = self._dbclient.set_latest_filter_state(self._dbclient.filterstate.COMPLETE)
                    if ret.state != error.SUCCEED:
                        return ret
                    continue

                self._logger.debug(f"block({blockhash}) height:{version}  txid count = {len(txids)}")
                if latest_saved_txid is not None and len(latest_saved_txid) > 0:
                    index = txids.index(latest_saved_txid)
                    assert index >= 0, \
                            f"not found txid({latest_saved_txid}), check data info."
                    txids = txids[index + 1:]

                    self._logger.debug(f"prune txids start: {index + 1}  len: {len(txids)}")
                    ##only restart check
                    latest_saved_txid = None

                    #remove datas with txid == latest_saved_ver  ????

                    #some txid is saved, next txid..


                for txid in txids:
                    if self.work() == False:
                        self._logger.debug(f"will stop work, next height: {version + 1}")

                    ret = self._vclient.getrawtransaction(txid = txid)
                    assert ret.state == error.SUCCEED, f"get raw transaction failed.txid = {txid}"
                    tran = ret.datas
                    tran["hex"] = ""

                    tran_size = (tran.get("vinsize", 0) + tran.get("voutsize", 0))
                    use_session = True
                    session = None
                    if tran_size >= 500: #transaction size must be < 16M
                        use_session = False

                    with self._dbclient.start_session(causal_consistency=True) as sessiondb:
                       with sessiondb.start_transaction():
                            if use_session:
                                session = sessiondb

                            if self.map_to_local:
                                ret = self.save_transaction(txid, tran, blockhash, session=session)
                                assert ret.state == error.SUCCEED, f"save transaction failed.txid = {txid}"

                            if self.map_to_local:
                                ret = self._vclient.gettxoutinfromdata(tran)
                                assert ret.state == error.SUCCEED, f"get transaction vout and vin failed.{txid}"

                                txoutin = ret.datas

                                ret = self.save_txout(txid, ret.datas.get("vout"), blockhash, session=session)
                                assert ret.state == error.SUCCEED, f"save txout failed.txid = {txid}"

                                ret = self.update_txout_state(txoutin.get("vin"), blockhash, session=session)
                                assert ret.state == error.SUCCEED, f"update txout failed.txid = {txid}"
                            
                            if self.store_op_tran:
                                #ret = self.get_opreturn(txoutin.get("vout"))
                                ret = self._vclient.getopreturnfromdata(tran)
                                if ret.state == error.SUCCEED and ret.datas is not None:
                                    ret = payload_parse.is_valid_violas(ret.datas)
                                    if ret.state == error.SUCCEED and ret.datas:
                                        ret = self.save_opreturn_txid(latest_opreturn_index, txid, session=session)
                                        assert ret.state == error.SUCCEED, f"save address map txout failed.txid = {txid}"

                                        ret = self._dbclient.set_latest_opreturn_index(latest_opreturn_index, session = session)
                                        assert ret.state == error.SUCCEED, f"save opreturn index failed. txid = {txid}"

                                        self._logger.debug(f"save opreturn height: {version}, txid :{txid}")
                                        latest_opreturn_index = latest_opreturn_index + 1

                            #set latest saved txid
                            ret = self._dbclient.set_latest_saved_txid(txid,session=session)
                            assert ret.state == error.SUCCEED, f"update latest saved txid failed.txid = {txid}"
                            #proof
                            self._logger.debug(f"transaction parse is succeed. height:{version} txid:{txid}")

                latest_filter_state = self._dbclient.filterstate.COMPLETE
                ret = self._dbclient.set_latest_filter_state(self._dbclient.filterstate.COMPLETE)
                #reset state for COMPLETE -- must be
                if ret.state != error.SUCCEED:
                    return ret
                #save to redis db
                self._logger.info(f"parse transaction . height: {version}")
                version = version + 1
 
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        finally:
            self._logger.debug("end filter work")
        return ret


def works():
    filter = afilter(name, stmanage.get_db("base"),  stmanage.get_btc_conn())
    filter.set_min_valid_version(1722193)
    filter.set_step(1)
    def signal_stop(signal, frame):        
        filter.stop()
    try:
        signal.signal(signal.SIGINT, signal_stop)
        signal.signal(signal.SIGTSTP, signal_stop)
        signal.signal(signal.SIGTERM, signal_stop)
        ret = filter.start()
        if ret.state != error.SUCCEED:
            print(ret.message)

    except Exception as e:
        ret = parse_except(e)
    return ret

if __name__ == "__main__":
    works()
