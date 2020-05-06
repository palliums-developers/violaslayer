#!/usr/bin/python3
'''
btc exchange vtoken db
'''
import operator
import sys,os
sys.path.append(os.getcwd())
import traceback
import datetime
import sqlalchemy
import stmanage
import random
import redis
import json
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
name="dbvproof"

#load logging

class dbvproof(dbvbase):
    __KEY_MIN_VERSION_START = "min_version_start"
    def __init__(self, name, hosts, db, user = None, password = None, 
            authdb = 'admin', rsname = None, newdb = False):
        dbvbase.__init__(self, name = name, hosts = hosts, db = db, user = user, password = password, 
                authdb = authdb, rsname = rsname, newdb = newdb)

    def __del__(self):
        dbvbase.__del__(self)

    def set_proof(self, tran_id, value):
        try:
            version = value.get("version", None)
            if version is None or version < 0:
                return result(error.ARG_INVALID, "tran id is invalid.")

            value["_id"] = version
            ret = self.insert_many([value, {"_id":tran_id, "version":version}])
           
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_proof(self, tran_id, value):
        try:
            ret = self.find_with_id(tran_id)
            if ret.state != error.SUCCEED:
                return ret

            version = ret.get("version")
            if version is None or version < 0:
                return result(error.DB_PROOF_INFO_INVALID, f"not fount transaction({tran_id}).")

            value["_id"] = version
            ret = self.updata_one(value)
        except Exception as e:
            ret = parse_except(e)
        return ret


    def set_proof_min_version_for_start(self, version):
        try:
            ret = self.set(self.__KEY_MIN_VERSION_START, version)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_proof_min_version_for_start(self):
        try:
            ret = self.get(self.__KEY_MIN_VERSION_START)
            if ret.state == error.SUCCEED:
                if ret.datas is None:
                    ret = result(error.SUCCEED, "", '0')
        except Exception as e:
            ret = parse_except(e)
        return ret

