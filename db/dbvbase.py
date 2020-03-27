#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
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

#module name
name="dbvbase"

class dbvbase(baseobject, pymongo.MongoClient):
    __key_latest_filter_ver     = "latest_filter_ver"
    __key_latest_saved_ver      = "latest_saved_ver"
    __key_min_valid_ver         = "min_valid_ver"


    def __init__(self, name, host, port, db, user = None, password = None, authdb = 'admin', newdb = False):
        baseobject.__init__(self, name)
        self.__host = host
        self.__port = port
        self.__db_name = db
        self.__collection_name = None
        self.__authdb = authdb
        self.__password = password
        self.__user = user
        self._client = None
        self._collection = None
        ret = self.__connect(host, port, db, user, password, authdb, newdb)
        if ret.state != error.SUCCEED:
            raise Exception(f"connect db({db}) failed")

    def __del__(self):
        pass

    @property
    def db_name(self):
        return self._db

    @property
    def collection_name(self):
        return self.__collection_name

    def __connect(self, host, port, db, user = None, password = None, authdb = 'admin', newdb = False):
        try:
            self._logger.debug(f"connect db(host={host}, port={port}, db={db}, user = {user}, password={password}, authdb={authdb}, newdb={newdb})")
            login = ""
            if user is not None or password is None:
                login = f"{parse.quote_plus(user)}:{parse.quote_plus(password)}@"
            uri = f"mongodb://{login}{host}:{port}/{authdb}"

            pymongo.MongoClient.__init__(self, uri)
            self.use_db(db, newdb)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def use_collection(self, collection, create = False):
        if create == False and db not in self.list_collection_names().datas:
            raise Exception(f"not found collection({collection}).")
        self.__collection_name = collection
        self._collection = self._client[collection]

    def use_db(self, db, create = False):
        if create == False and db not in self.list_database_names().datas:
            raise Exception(f"not found db({db}).")

        self.__db = db
        self._client =  self.get_database(db)

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
            ret = self.get("mod_name")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_mod_name(self, name):
        try:
            ret = self.set("mod_name", name)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find(self, key):
        try:
            datas = self._collection.find(key)
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
            ret = self.find_one({"_id": id})
        except Exception as e:
            ret = parse_except(e)
        return ret
    def update(self, key, value, multi = True):
        try:
            self._collection.update(key, {"$set":{value}}, multi)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self, id, value):
        try:
            datas = dict(value)
            if datas.get("_id") is None:
                datas["_id"] = id
            elif id != datas.get("_id"):
                return result(error.ARG_INVALID, f"id({id}) and value['_id']({value['_id']}) is not match.")
            self._collection.save(datas)   
            ret = result(error.SUCCEED)

        except Exception as e:
            ret = parse_except(e)
        return ret


    def insert_one(self, value):
        try:
            self._collection.insert_one(value)   
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def insert_many(self, value):
        try:
            self._collection.insert_many(value)   
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret
    def is_exists(self, key):
        try:
            datas = self.find(key)
            ret = result(error.SUCCEED, "", len(datas) > 0)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def remove(self, key):
        try:
            self._collection.remove(key)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def remove_with_id(self, id):
        try:
            ret = self.remove({"_id": id})
        except Exception as e:
            ret = parse_except(e)
        return ret
    def remove_all(self):
        try:
            ret = self.remove({})
        except Exception as e:
            ret = parse_except(e)
        return ret

    def count(self, key):
        try: 
            self._collection.count(key)
            ret = result(error.SUCCEED)
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

    def set_latest_filter_ver(self, ver):
        try:
            self._client.set(self.__key_latest_filter_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_filter_ver(self):
        try:
            datas = self._client.get(self.__key_latest_filter_ver)
            if datas is None:
                datas = '-1'
            ret = result(error.SUCCEED, "", int(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_latest_saved_ver(self, ver):
        try:
            self._client.set(self.__key_latest_saved_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_latest_saved_ver(self):
        try:
            datas = self._client.get(self.__key_latest_saved_ver)
            if datas is None:
                datas = '-1'
            ret = result(error.SUCCEED, "", int(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def list_version_keys(self, start = 0):
        keys = self.keys().datas
        return  sorted([int(key) for key in keys if key.isdigit() and int(key) >= start])

    def get_min_valid_ver(self):
        try:
            datas = self._client.get(self.__key_min_valid_ver)
            if datas is None:
                datas = '0'
            ret = result(error.SUCCEED, "", int(datas))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def set_min_valid_ver(self, ver):
        try:
            self._client.set(self.__key_min_valid_ver, ver)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

def test_db():
    client = dbvbase(name = name, host = "127.0.0.1", port = 37017, db = "test", user = "violas", password = "violas@palliums", newdb = True)
    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)

    client.use_collection("baseinfo", create = True)

    client.remove_all()

    client.save("0001", {"name": "xml", "age":10, "sex":"cp"})
    client.save("0002", {"name": "json", "age":11, "sex":"cp"})
    client.save("0003", {"name": "c++", "age":12, "sex":"cp"})
    for data in client.find_all().datas:
        print(f"find all:{data}")

    print("*" * 30)
    client.remove_with_id("0001")
    for data in client.find_all().datas:
        print(f"find all:{data}")

    print("*" * 30)
    client.remove({"_id":"0003"})
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

    client.use_collection("sub", create = True)
    client.insert_one({"_id":"1002", "name": "json", "age":11, "sex":"cp"})
    client.use_collection("baseinfo", create = True)

    print("*" * 30)
    client.remove_all()
    for data in client.find_all().datas:
        print(f"find all:{data}")

    print(client.list_database_names().datas)
    print(client.list_collection_names().datas)

    print("*" * 30 + "drop collection baseinfo")
    client.drop_collection("baseinfo")
    print(client.list_collection_names().datas)

    print("*" * 30 + "drop collection sub")
    client.drop_collection("sub")
    print(client.list_collection_names().datas)

    print("*" * 30 + "drop db test")
    client.drop_db("test")
    print(client.list_database_names().datas)

    

if __name__ == "__main__":
    test_db()
