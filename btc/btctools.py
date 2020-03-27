#!/usr/bin/python3
import operator
import sys, getopt
import json
import os
sys.path.append(os.getcwd())
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import stmanage
import requests
import comm
import comm.error
import comm.result
from comm.result import result
from comm.error import error
from comm.parseargs import parseargs
from comm.functions import json_print
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btc.btcclient import btcclient
from enum import Enum

#module name
name="btctools"

#load logging
logger = log.logger.getLogger(name) 

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def btchelp():
    client = getbtcclient()
    ret = client.help()
    assert ret.state == error.SUCCEED, " btchelp failed"
    print(ret.datas)

def getblockcount():
    client = getbtcclient()
    ret = client.getblockcount()
    assert ret.state == error.SUCCEED, f"getblockcount() failed"
    print(f"block count:{ret.datas}")

def getblockhash(index):
    client = getbtcclient()
    ret = client.getblockhash(index)
    assert ret.state == error.SUCCEED, f"getblockhash({index}) failed"
    print(f"blockhash({index}):{ret.datas}")

def getblockwithhash(blockhash):
    client = getbtcclient()
    ret = client.getblockwithhash(blockhash)
    assert ret.state == error.SUCCEED, f"getblockwithhash({blockhash}) failed"
    json_print(ret.datas)

def getblockwithindex(index):
    client = getbtcclient()
    ret = client.getblockwithindex(index)
    assert ret.state == error.SUCCEED, f"getblockwithindex({index}) failed"
    json_print(ret.datas)

def getblocktxidswithindex(index):
    client = getbtcclient()
    ret = client.getblocktxidswithindex(index)
    assert ret.state == error.SUCCEED, f"getblocktxidswithindex({index}) failed"
    json_print(ret.datas)

def getblocktxidswithhash(blockhash):
    client = getbtcclient()
    ret = client.getblocktxidswithhash(blockhash)
    assert ret.state == error.SUCCEED, f"getblocktxidswithhash({blockhash}) failed"
    json_print(ret.datas)

def getrawtransaction(txid, verbose = True, blockhash = None):
    client = getbtcclient()
    ret = client.getrawtransaction(txid, verbose, blockhash)
    assert ret.state == error.SUCCEED, f"getrawtransaction({txid}, {verbose}, {blockhash}) failed"
    json_print(ret.datas)

def gettxoutin(txid):
    client = getbtcclient()
    ret = client.gettxoutin(txid)
    assert ret.state == error.SUCCEED, f"gettxoutin({txid}) failed"
    json_print(ret.datas)

def gettxoutwithn(txid, n):
    client = getbtcclient()
    ret = client.gettxoutwithn(txid, n)
    assert ret.state == error.SUCCEED, f"gettxoutwithn({txid}, {n}) failed"
    json_print(ret.datas)

def init_args(pargs):
    pargs.append("help", "show arg list")
    pargs.append("getblockcount", "get block count.")
    pargs.append("getblockhash", "get block hash.", True, ["index"])
    pargs.append("getblockwithhash", "get block info with blockhash.", True, ["blockhash"])
    pargs.append("getblockwithindex", "get block info with index.", True, ["index"])
    pargs.append("getblocktxidswithhash", "get block txid list with blockhash.", True, ["blockhash"])
    pargs.append("getblocktxidswithindex", "get block txid list with index.", True, ["index"])
    pargs.append("getrawtransaction", "get raw transaction", True, ["txid", "verbose", "blockhash"])
    pargs.append("gettxoutin", "get transaction vin and vout", True, ["txid"])
    pargs.append("gettxoutwithn", "get transaction vout[n]", True, ["txid", "n"])

def run(argc, argv):
    try:
        logger.debug("start btc.main")
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
        if pargs.is_matched(opt, ["btchelp"]):
            ret = btchelp()
        elif pargs.is_matched(opt, ["getblockcount"]):
            ret = getblockcount()
        elif pargs.is_matched(opt, ["getblockhash"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getblockhash(int(arg_list[0]))
        elif pargs.is_matched(opt, ["getblockwithhash"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getblockwithhash(arg_list[0])
        elif pargs.is_matched(opt, ["getblockwithindex"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getblockwithindex(int(arg_list[0]))
        elif pargs.is_matched(opt, ["getblocktxidswithhash"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getblocktxidswithhash(arg_list[0])
        elif pargs.is_matched(opt, ["getblocktxidswithindex"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getblocktxidswithindex(int(arg_list[0]))
        elif pargs.is_matched(opt, ["getrawtransaction"]):
            if len(arg_list) not in (1, 2, 3):
                pargs.exit_error_opt(opt)
            txid = None
            verbose = True
            blockhash= None
            if len(arg_list) >= 1:
                txid = arg_list[0]
            if len(arg_list) >= 2:
                verbose = arg_list[1] == "True"
            if len(arg_list) >= 2:
                blockhash = arg_list[2]
            ret = getrawtransaction(txid, verbose, blockhash)
        elif pargs.is_matched(opt, ["gettxoutin"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = gettxoutin(arg_list[0])
        elif pargs.is_matched(opt, ["gettxoutwithn"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = gettxoutwithn(arg_list[0], int(arg_list[1]))

    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
