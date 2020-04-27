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

    def set_proof(self, key, value):
        try:
            if "_id" not in value:
                value["_id"] = key
            ret = self.insert_one(value)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def update_proof(self, key, value):
        try:
            if "_id" not in value:
                value["_id"] = key
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

