#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os, json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import random
import redis
from comm.error import error
from comm.result import result, parse_except
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, UniqueConstraint, Index, String
from db.dbvbase import dbvbase

from enum import Enum

#module name
name="dbvfilter"

class dbvfilter(dbvbase):
    def __init__(self, name, hosts, db, user = None, password = None, 
            authdb = 'admin', rsname = None, newdb = False):
        dbvbase.__init__(self, name = name, hosts = hosts, db = db, user = user, password = password, 
                authdb = authdb, rsname = rsname, newdb = newdb)

    def __del__(self):
        dbvbase.__del__(self)

    def set_mempool_buf(self, datas, session = None):
        try:
            coll = self.get_collection("mempool", create = True)
            data_val = json.dumps([data for data in datas])
            coll.update_many({"_id":"txidxs"}, {"$set":{"txidxs":data_val}}, upsert = True, session=session)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_mempool_buf(self):
        try:
            coll = self.get_collection("mempool", create = True)
            ret = coll.find_one({"_id": "txidxs"})

            ret = result(error.SUCCEED, datas = json.loads(ret.get("txidxs", {""})))
        except Exception as e:
            ret = parse_except(e)
        return ret
