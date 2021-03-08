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
    print(f"db list: {stmanage.list_db_name()}")
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
    print(f"cleandb({dbs})")
    for name in dbs:
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
    pargs.append(showaddressesinfo, "show btc addresses txout db info.")
    pargs.append(cleanaddresses, "clean btc addresses db.")
    pargs.append(showdbinfo, f"show db({stmanage.list_db_name()}) info.")
    pargs.append(cleandb, f"clean db({stmanage.list_db_name()}).")

def run(argc, argv):
    try:
        logger.debug("start managedb.main argv: {argv}")
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
        count, arg_list = pargs.split_arg(opt, arg)
        print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["cleandb"]):
            if len(arg_list) < 1:
                pargs.exit_error_opt(opt)
            cleandb(arg_list)
        elif pargs.has_callback(opt):
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt: {opt}")

    logger.debug("end managedb.main")

if __name__ == "__main__":
    stmanage.set_conf_env("../violaslayer.toml")
    run(len(sys.argv) - 1, sys.argv[1:])
