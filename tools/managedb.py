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

def get_basedb():
    return managedb(name, stmanage.get_db("base"))

def get_exproofdb():
    return managedb(name, stmanage.get_db("exproof"))

def get_addressesdb():
    return managedb(name, stmanage.get_db("addresses"))

def showbaseinfo():
    dbclient = get_basedb()
    dbclient.use_collection("datainfo")

    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleanbase():
    dbclient = get_basedb()
    dbclient.drop_db("base")

def showexproofinfo():
    dbclient = get_exproofdb()
    dbclient.use_collection("datainfo")
    ret = dbclient.get_state_info()
    json_print(ret.datas)

def cleanexproof():
    dbclient = get_basedb()
    dbclient.drop_db("exproof")

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
    pargs.append("showbaseinfo", "clean btc base db info.")
    pargs.append("cleanbase", "clean btc base db.")
    pargs.append("showexproofinfo", "show btc exproof db info.")
    pargs.append("cleanexproof", "clean btc exproof db.")
    pargs.append("cleanaddresses", "clean btc addresses db.")


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
        elif pargs.is_matched(opt, ["showexproofinfo"]):
            ret = showexproofinfo()
        elif pargs.is_matched(opt, ["cleanexproof"]):
            ret = cleanexproof()
        elif pargs.is_matched(opt, ["cleanaddresses"]):
            ret = cleanaddresses()

    logger.debug("end managedb.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
