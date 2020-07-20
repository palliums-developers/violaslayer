#!/usr/bin/python3
import operator
import sys, os, getopt
import json
sys.path.append("..")
sys.path.append(os.getcwd())
import hashlib
import traceback
import log
import log.logger
import traceback
import datetime
import sqlalchemy
import requests
import stmanage
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from btc.btcclient import btcclient
from enum import Enum
from db.dbvbase import dbvbase
from baseobject import baseobject
from comm.parseargs import parseargs
from comm.functions import json_print

#module name
name="managedb"
#load logging
logger = log.logger.getLogger(name) 

class managedb(dbvbase):
    def __init__(self, name, rconf):
        dbvbase.__init__(self, name, rconf.get("host", "127.0.0.1:37017"), rconf.get("db"), rconf.get("user", None), rconf.get("password", None), rconf.get("authdb", "admin"), rsname=rconf.get("rsname","rsviolas"))

def get_db(db):
    if db not in stmanage.list_db_name():
        raise f"db({db}) not found."

    return managedb(name, stmanage.get_db(db))

def get_basedb():
    return get_db("base")

def get_b2vproofdb():
    return get_db("b2vproof")

def get_addressesdb():
    return get_db("addresses")

def showbaseinfo():
    dbclient = get_basedb()
    dbclient.use_collection("datainfo")

    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleanbase():
    dbclient = get_basedb()
    dbclient.drop_db("base")

def showb2vproofinfo():
    dbclient = get_b2vproofdb()
    dbclient.use_collection("datainfo")
    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleanb2vproof():
    dbclient = get_b2vproofdb()
    dbclient.drop_db("b2vproof")

def showdbinfo(db):
    dbclient = get_db(db)
    dbclient.use_collection("datainfo")

    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleandb(dbs):
    for name in dbs:
        print(name)
        dbclient = get_db(name)
        dbclient.drop_db(name)

def showaddressesinfo():
    dbclient = get_addressesdb()
    dbclient.use_collection("datainfo")

    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleanaddresses():
    dbclient = get_addressesdb()
    dbclient.drop_db("addresses")

def init_args(pargs):
    pargs.append("help", "show arg list")
    pargs.append("showaddressesinfo", "show btc addresses txout db info.")
    pargs.append("cleanaddresses", "clean btc addresses db.")
    pargs.append("showdbinfo", f"show db({stmanage.list_db_name()}) info.", True, ["db name"])
    pargs.append("cleandb", f"clean db({stmanage.list_db_name()}).", True, ["db name"])

def run(argc, argv):
    try:
        logger.debug("start managedb.main")
        pargs = parseargs()
        init_args(pargs)
        pargs.show_help(argv)
        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        sys.exit(2)
    except Exception as e:
        logger.error(e)
        sys.exit(2)

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    for opt, arg in opts:
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["showbaseinfo"]):
            ret = showbaseinfo()
        elif pargs.is_matched(opt, ["cleanbase"]):
            ret = cleanbase()
        elif pargs.is_matched(opt, ["showb2vproofinfo"]):
            ret = showb2vproofinfo()
        elif pargs.is_matched(opt, ["cleanb2vproof"]):
            ret = cleanb2vproof()
        elif pargs.is_matched(opt, ["showaddressesinfo"]):
            ret = showaddressesinfo()
        elif pargs.is_matched(opt, ["cleanaddresses"]):
            ret = cleanaddresses()
        elif pargs.is_matched(opt, ["showdbinfo"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = showdbinfo(arg_list[0])
        elif pargs.is_matched(opt, ["cleandb"]):
            if len(arg_list) < 1:
                pargs.exit_error_opt(opt)
            ret = cleandb(arg_list)

    logger.debug("end managedb.main")

if __name__ == "__main__":
    stmanage.set_conf_env_default()
    run(len(sys.argv) - 1, sys.argv[1:])
