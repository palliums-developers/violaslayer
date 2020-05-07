#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
from functools import reduce
import sys,os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import random
import pymongo
from urllib import parse
from comm.error import error
from comm.result import result, parse_except
from baseobject import baseobject
from enum import Enum
from pymongo import ReadPreference
#module name
name="dbvbase"
class dbvbase(baseobject, pymongo.MongoClient):
    __key_latest_filter_ver     = "latest_filter_ver"
    __key_latest_filter_state   = "latest_filter_state"
    __key_latest_saved_ver      = "latest_saved_ver"
    __key_min_valid_ver         = "min_valid_ver"
    __key_latest_saved_txid     = "latest_saved_txid"
    __key_id_state_info         = "state_info"
    __key_latest_opreturn_index = "latest_opreturn_index"
    __name_datainfo             = "datainfo"
    class filterstate(Enum):
        START       = 1
        COMPLETE    = 2

    def __init__(self, name, hosts, db, user = None, password = None, authdb = 'admin', rsname = None, newdb = False):
        baseobject.__init__(self, name)
        self.__hosts = hosts
        self.__db_name = db
        self.__collection_name = None
        self.__authdb = authdb
        self.__rsname = rsname
        self.__password = password
        self.__user = user
        self._client = None
        self._collection = None
        ret = self.__connect(hosts, db, user, password, authdb, rsname, newdb)
        if ret.state != error.SUCCEED:
            raise Exception(f"connect db({db}) failed")

    def __del__(self):
        pass

    @property
    def db_pos(self):
        return f"{self.__hosts}.{self.db_name}.{self.collection_name}"

    @property
    def db_name(self):
        return self.__db_name

    @property
    def collection_name(self):
        return self.__collection_name

    def use_collection_datas(self):
        return self.use_collection("datas", True)

    def use_default_collections(self):
        if self.collection_name != self.__name_datainfo:
            self.use_collection(self.__name_datainfo, True)

    def __get_connect_db_uri(self, hosts, user, password, authdb, rsname):
        login = ""
        host = ",".join(hosts)
        if user is not None or password is None:
            login = f"{parse.quote_plus(user)}:{parse.quote_plus(password)}@"
        uri = f"mongodb://{login}{host}"
        if authdb is not None:
            uri += f"/{authdb}"
        if rsname is not None:
            uri += f"?replicaSet={rsname}"
        return uri

    def __connect(self, hosts, db, user = None, password = None, authdb = 'admin', rsname = None, newdb = False):
        try:
            self._logger.debug(f"connect db(hosts={hosts}, db={db}, user = {user}, password={password}, authdb={authdb}, newdb={newdb})")
            uri = self.__get_connect_db_uri(hosts = hosts, user = user, password = password, authdb = authdb, rsname = rsname)
            pymongo.MongoClient.__init__(self, uri, retryWrites=False, appname="violaslayer", readPreference="secondaryPreferred")
            self.use_db(db, newdb)
            self.use_collection("datainfo", newdb)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def use_collection(self, collection, create = False):
        if create == False and collection not in self.list_collection_names().datas:
            raise Exception(f"not found collection({collection}).")
        self.__collection_name = collection
        self._collection = self._client[collection]

    @property
    def collection(self):
        return self._collection

    def get_collection(self, collection, create = False):
        if create == False and db not in self.list_collection_names().datas:
            raise Exception(f"not found collection({collection}).")
        return self._client[collection]

    def use_db(self, db, create = False):
        if create == False and db not in self.list_database_names().datas:
            raise Exception(f"not found db({db}).")
        self.__db = db
        self._client =  self.get_database(db, read_preference=ReadPreference.SECONDARY_PREFERRED)

    @property 
    def database(self):
        return self._client

    def list_collection_names(self):
        try:
            ret = result(error.SUCCEED, "", self._client.list_collection_names())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def list_database_names(self):
        try:
            ret = result(error.SUCCEED, "",  super().list_database_names())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_mod_name(self):
        try:
            ret = result(error.SUCCEED, "", self.db_name)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find(self, key):
        try:
            datas = self.collection.find(key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_all(self):
        try:
            ret = self.find({})
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_with_id(self, id):
        try:
            datas = self.collection.find_one({"_id": id})
            if datas is None:
                datas = {}
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update(self, key, value, upsert = True, session=None):
        try:
            self._collection.update_many(key, {"$set":value}, upsert = upsert, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_with_id(self, id, value, session=None):
        try:
            print(f"id:{id} vlaue={value}")
            ret = self.update({"_id":id}, value, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def increase(self, key, value, upsert = True, session=None):
        try:
            self._collection.update_many(key, {"$inc":value}, upsert = upsert, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def increase_with_id(self, id, value, session=None):
        try:
            ret = self.increase({"_id":id}, value, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def push(self, key, value, upsert = True, session=None):
        try:
            self._collection.update_many(key, {"$push":value}, upsert = upsert, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def push_with_id(self, id, value, session=None):
        try:
            ret = self.increase({"_id":id}, value, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self, id, value, session=None):
        try:
            datas = dict(value)
            if datas.get("_id") is None:
                datas["_id"] = id
            elif id != datas.get("_id"):
                return result(error.ARG_INVALID, f"id({id}) and value['_id']({value['_id']}) is not match.")
            self._collection.replace_one({"_id":id}, value, session=session)   
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_one(self, value, session=None):
        try:
            self._collection.insert_one(value, session=session)   
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_many(self, value, session = None):
        try:
            self._collection.insert_many(value, session=session)   
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_exists(self, key):
        try:
            ret = result(error.SUCCEED, "", self.collection.find_one(key) is not None)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def key_is_exists(self, key):
        return self.is_exists(key)

    def delete_one(self, key, session=None):
        try:
            self._collection.delete_one(key, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def delete_many(self, key, session=None):
        try:
            self._collection.delete_many(key, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def delete_with_id(self, id, session=None):
        try:
            ret = self.delete_one({"_id": id}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def delete_all(self, session=None):
        try:
            ret = self.delete_many({}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def count(self, key):
        try: 
            datas = self._collection.count(key)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def count_all(self):
        try: 
            ret = self.count({})
        except Exception as e:
            ret = parse_except(e)
        return ret

    def drop_collection(self, name):
        try:
            collection = self._client[name]
            collection.drop()
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def drop_db(self, name):
        try:
            db = self.drop_database(name)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_state_info(self, value, session = None):
        try:
            self.use_default_collections()
            self.update_with_id(self.__key_id_state_info, value, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_state_info(self, key = None, defvalue = None):
        try:
            self.use_default_collections()
            ret = self.find_with_id(self.__key_id_state_info)
            if ret.state != error.SUCCEED:
                return ret

            if key is not None:
                ret = result(error.SUCCEED, "", ret.datas.get(key, defvalue))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_filter_state(self, state, session=None):
        try:
            ret = self.set_state_info({self.__key_latest_filter_state:state.name}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_filter_state(self):
        try:
            ret = self.get_state_info(self.__key_latest_filter_state, self.filterstate.COMPLETE.name)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_filter_ver(self, ver, session=None):
        try:
            ret = self.set_state_info({self.__key_latest_filter_ver:ver, self.__key_latest_filter_state:self.filterstate.START.name, self.__key_latest_saved_txid:""}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_filter_ver(self):
        try:
            ret = self.get_state_info(self.__key_latest_filter_ver, -1)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_saved_ver(self, ver, session=None):
        try:
            ret = self.set_state_info({self.__key_latest_saved_ver:ver}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_saved_ver(self):
        try:
            ret = self.get_state_info(self.__key_latest_saved_ver, -1)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_saved_txid(self, txid, session=None):
        try:
            ret = self.set_state_info({self.__key_latest_saved_txid:txid}, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_saved_txid(self):
        try:
            ret = self.get_state_info(self.__key_latest_saved_txid)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_min_valid_ver(self, ver, session=None):
        try:
            self.use_default_collections()
            ret = self.save(self.__key_id_state_info, {self.__key_min_valid_ver: ver}, session=session)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_min_valid_ver(self):
        try:
            self.use_default_collections()
            ret = self.find_with_id(self.__key_id_state_info)
            if ret.state != error.SUCCEED:
                return ret
            ret = result(error.SUCCEED, "", ret.datas.get(self.__key_min_valid_ver, 0))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_opreturn_index(self, index, session=None):
        try:
            ret = self.set_state_info({self.__key_latest_opreturn_index: index}, session=session)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_opreturn_index(self):
        try:
            ret = self.get_state_info(self.__key_latest_opreturn_index, -1)
        except Exception as e:
            ret = parse_except(e)
        return ret

def test_write_db():
    hosts = ["127.0.0.1:37018", "127.0.0.1:37018"]
    hosts = ["52.231.74.79:37017", "18.136.139.151:37017", "18.136.139.151:37018"]
    client = dbvbase(name = name, hosts = hosts, db = "test", user = "violas", password = "violas@palliums", rsname="rsviolas", newdb = True)
    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)
    client.use_collection("baseinfo", create = True)
    #client.collection.create_index([("_id", pymongo.ASCENDING)], name="idx_bi_id")
    #client.collection.create_index([("name", pymongo.ASCENDING)], name="idx_bi_name")
    #client.collection.create_index([("age", pymongo.ASCENDING)], name="idx_bi_age")
    client.save("0001", {"name": "xml", "age":10, "sex":"cp"})
    client.save("0002", {"name": "json", "age":11, "sex":"cp"})
    client.save("0003", {"name": "c++", "age":12, "sex":"cp"})
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.insert_one({"_id":"1002", "name": "json", "age":11, "sex":"cp"})
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.insert_many([{"_id":"2002", "name": "js", "age":11, "sex":"cp"}, \
            {"_id": "2001", "name": "lua", "age":"8"}
            ])
    print("*" * 30 + f" collection sub")
    client.use_collection("sub", create = True)
    client.insert_one({"_id":"1002", "name": "json", "age":11, "sex":"cp"})
    client.set_latest_filter_ver(3)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_latest_filter_ver().datas)
    client.use_collection("baseinfo", create = True)
    print("*"*30 + "index index_information")
    print(client.collection.index_information())
    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)
    client.set_min_valid_ver(1)
    print(client.get_min_valid_ver().datas)
    print("*" * 30 + "get latest saved ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.set_latest_saved_ver(2)
    print(client.get_latest_saved_ver().datas)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.set_latest_filter_ver(3)
    print(client.get_latest_filter_ver().datas)

    client.use_collection("sub", create = True)
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    for data in client.find_all().datas:
        print(f"find all:{data}")

    client.use_collection("baseinfo", create = True)
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    for data in client.find_all().datas:
        print(f"find all:{data}")

    print("*" * 30)
    print(f"client address: {client.address}")
    print(f"collection red_preference: {client.collection.read_preference}")

def test_read_db():
    hosts = ["127.0.0.1:37018", "127.0.0.1:37018"]
    hosts = ["52.231.74.79:37017", "18.136.139.151:37017", "18.136.139.151:37018"]
    client = dbvbase(name = name, hosts = hosts, db = "test", user = "violas", password = "violas@palliums", rsname="rsviolas", newdb = True)
    client.use_collection("baseinfo", create = True)
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print(f"client address: {client.address}")
    print("*" * 30)
    client.use_collection("sub", create = True)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_latest_filter_ver().datas)
    client.use_collection("baseinfo", create = True)
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30 + "get min valid ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_min_valid_ver().datas)
    print("*" * 30 + "get latest saved ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_latest_saved_ver().datas)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_latest_filter_ver().datas)
    print(f"client address: {client.address}")
    print(f"collection red_preference: {client.collection.read_preference}")

def test_db():
    hosts = ["127.0.0.1:37018", "127.0.0.1:37018"]
    hosts = ["52.231.74.79:37017", "18.136.139.151:37017", "18.136.139.151:37018"]
    client = dbvbase(name = name, hosts = hosts, db = "test", user = "violas", password = "violas@palliums", rsname="rsviolas", newdb = True)
    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)
    client.use_collection("baseinfo", create = True)
    client.delete_all()
    #client.collection.create_index([("_id", pymongo.ASCENDING)], name="idx_bi_id")
    #client.collection.create_index([("name", pymongo.ASCENDING)], name="idx_bi_name")
    #client.collection.create_index([("age", pymongo.ASCENDING)], name="idx_bi_age")
    client.save("0001", {"name": "xml", "age":10, "sex":"cp"})
    client.save("0002", {"name": "json", "age":11, "sex":"cp"})
    client.save("0003", {"name": "c++", "age":12, "sex":"cp"})
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.delete_with_id("0001")
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.delete_one({"_id":"0003"})
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.insert_one({"_id":"1002", "name": "json", "age":11, "sex":"cp"})
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30)
    client.insert_many([{"_id":"2002", "name": "js", "age":11, "sex":"cp"}, \
            {"_id": "2001", "name": "lua", "age":"8"}
            ])
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print("*" * 30 + f" collection sub")
    client.use_collection("sub", create = True)
    client.insert_one({"_id":"1002", "name": "json", "age":11, "sex":"cp"})
    client.set_latest_filter_ver(3)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    print(client.get_latest_filter_ver().datas)
    client.use_collection("baseinfo", create = True)
    print("*"*30 + "index index_information")
    print(client.collection.index_information())
    print("*" * 30)
    client.delete_all()
    for data in client.find_all().datas:
        print(f"find all:{data}")
    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)
    print("*" * 30 + f"drop collection baseinfo.")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.drop_collection("baseinfo")
    print(client.list_collection_names().datas)
    print("*" * 30 + "get min valid ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.set_min_valid_ver(1)
    print(client.get_min_valid_ver().datas)
    print("*" * 30 + "get latest saved ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.set_latest_saved_ver(2)
    print(client.get_latest_saved_ver().datas)
    print("*" * 30 + "get latest filter ver")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.set_latest_filter_ver(3)
    print(client.get_latest_filter_ver().datas)
    print("*" * 30 + "drop collection sub")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.drop_collection("sub")
    print(client.list_collection_names().datas)
    print("*" * 30 + "drop db test")
    print(f"--> db name: {client.db_name}    collection name : {client.collection_name}")
    client.drop_db("test")
    print(client.list_database_names().datas)
    print(f"client address: {client.address}")
    print(f"collection red_preference: {client.collection.read_preference}")
if __name__ == "__main__":
    type = "a"
    print(sys.argv)
    if len(sys.argv) == 2:
        type = sys.argv[1]

    if type in ("r", "read"):
        test_read_db()
    elif type in ("w", "write"):
        test_write_db()
    elif type in("a", "all"):
        test_db()
    
