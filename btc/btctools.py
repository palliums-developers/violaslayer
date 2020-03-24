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
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from btc.btcclient import btcclient
from enum import Enum

#module name
name="btctools"

#load logging
logger = log.logger.getLogger(name) 

def getbtcclient():
    return btcclient(name, stmanage.get_btc_conn())

def sendtoaddress(address, count):
    client = getbtcclient()
    ret = client.sendtoaddress(address, count)
    assert ret.state == error.SUCCEED, " sendtoaddress failed"
    print(ret.datas)
    
def sendexproofstart(fromaddress, toaddress, amount, vaddress, sequence, vtoken):
    client = getbtcclient()
    ret = client.sendexproofstart(fromaddress, toaddress, amount, vaddress, sequence, vtoken)
    assert ret.state == error.SUCCEED, " sendexproofstart failed"
    print(ret.datas)

def sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version):
    client = getbtcclient()
    ret = client.sendexproofend(fromaddress, toaddress, vaddress, sequence, vamount, version)
    assert ret.state == error.SUCCEED, " sendexproofend failed"
    print(ret.datas)

def sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version):
    client = getbtcclient()
    ret = client.sendexproofmark(fromaddress, toaddress, toamount, vaddress, sequence, version)
    assert ret.state == error.SUCCEED, "sendexproofmark failed"
    print(ret.datas)

def generatetoaddress(count, address):
    client = getbtcclient()
    ret = client.generatetoaddress(count, address)
    assert ret.state == error.SUCCEED, " generatetoaddress failed"
    print(ret.datas)
    
def listunspent(minconf = 1, maxconf = 9999999, addresses = None, include_unsafe = True, query_options = None):
    client = getbtcclient()
    ret = client.listunspent(minconf, maxconf, addresses, include_unsafe, query_options)
    assert ret.state == error.SUCCEED, " listunspent failed"
    for data in ret.datas:
        print("address:{}, amount:{}".format(data["address"], data["amount"]))

def listexproofforstart(receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofforstart(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforstart failed"
    for data in ret.datas:
        print(data)

def listexproofforend(receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofforend(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofforend failed"
    for data in ret.datas:
        print(data)

def listexproofformark(receiver, excluded = None):
    client = getbtcclient()
    ret = client.listexproofformark(receiver, excluded)
    assert ret.state == error.SUCCEED, " listexproofformark failed"
    for data in ret.datas:
        print(data)

def listexproofforb2v(cursor, limit = 10):
    client = getbtcclient()
    ret = client.listexproofforb2v(cursor, limit)
    assert ret.state == error.SUCCEED, " listexproofforb2v failed"
    for data in ret.datas:
        print(data)

def btchelp():
    client = getbtcclient()
    ret = client.help()
    assert ret.state == error.SUCCEED, " btchelp failed"
    print(ret.datas)

def getwalletbalance():
    client = getbtcclient()
    ret = client.getwalletbalance()
    assert ret.state == error.SUCCEED, "getwalletbalance failed"
    print(f"wallet balance:{ret.datas:.8f}")

def getwalletaddressbalance(address):
    client = getbtcclient()
    ret = client.getwalletaddressbalance(address)
    assert ret.state == error.SUCCEED, " getwalletaddressbalance failed"
    print("wallet balance:{}".format(ret.datas))

def init_args(pargs):
    pargs.append("help", "show arg list")
    pargs.append("sendtoaddress", "send to address.format.", True, ["address", "count"])
    pargs.append("endexproofstart", "create new exchange start proof.", True, ["fromaddress", "toaddress", "amount", "vaddress", "sequence", "vtoken"])
    pargs.append("sendexproofend", "create new exchange end proof.", True, ["fromaddress", "toaddress", "vaddress", "sequence", "vamount", "version"])
    pargs.append("endexproofmark", "create new exchange mark proof.", True, ["fromaddress", "toaddress", "toamount", "vaddress", "sequence", "version"])
    pargs.append("generatetoaddress", "generate new block to address.", True, ["count", "address"])
    pargs.append("listunspent", "returns array of unspent transaction outputs.", True, ["minconf", "maxconf", "addresses", "include_unsafe", "query_options"])
    pargs.append("listexproofforstart", "returns array of proof state is start .", True, ["receiver"])
    pargs.append("listexproofforend", "returns array of proof state is end .", True, ["receiver"])
    pargs.append("listexproofformark", "returns array of proof state is mark .", True, ["receiver"])
    pargs.append("listexproofforb2v", "returns array of proof list type = b2v. .", True, ["cursor", "limit"])
    pargs.append("btchelp", "returns bitcoin-cli help.")
    pargs.append("getwalletbalance", "returns wallet balance.")
    pargs.append("getwalletaddressbalance", "returns wallet target address's balance.", True, ["address"])

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
        if pargs.is_matched(opt, ["sendtoaddress"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = sendtoaddress(arg_list[0], arg_list[1])
        elif pargs.is_matched(opt, ["sendexproofstart"]):
            if len(arg_list) != 6:
                pargs.exit_error_opt(opt)
            ret = sendexproofstart(arg_list[0], arg_list[1], float(arg_list[2]), arg_list[3], int(arg_list[4]), arg_list[5])
        elif pargs.is_matched(opt, ["sendexproofend"]):
            if len(arg_list) != 6:
                pargs.exit_error_opt(opt)
            ret = sendexproofend(arg_list[0], arg_list[1], arg_list[2], int(arg_list[3]), int(arg_list[4]), int(arg_list[5]))
        elif pargs.is_matched(opt, ["sendexproofmark"]):
            if len(arg_list) != 6:
                pargs.exit_error_opt(opt)
            ret = sendexproofmark(arg_list[0], arg_list[1], arg_list[2], arg_list[3], int(arg_list[4]), int(arg_list[5]))
        elif pargs.is_matched(opt, ["generatetoaddress"]):
            if len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            ret = generatetoaddress(int(arg_list[0]), arg_list[1])
        elif pargs.is_matched(opt, ["listunspent"]):
            if len(arg_list) != 5 and len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            if len(arg_list) != 2:
                ret = listunspent(int(arg_list[0]), int(arg_list[1]), arg_list[2], arg_list[3], arg_list[4])
            else:
                ret = listunspent(int(arg_list[0]), int(arg_list[1]))
        elif pargs.is_matched(opt, ["listexproofforstart"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = listexproofforstart(arg_list[0])
        elif pargs.is_matched(opt, ["listexproofforend"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = listexproofforend(arg_list[0])
        elif pargs.is_matched(opt, ["listexproofformark"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = listexproofformark(arg_list[0])
        elif pargs.is_matched(opt, ["listexproofforb2v"]):
            if len(arg_list) != 1 and len(arg_list) != 2:
                pargs.exit_error_opt(opt)
            if len(arg_list) == 2:
                limit = int(arg_list[1])
                ret = listexproofforb2v(int(arg_list[0]), limit)
            else:
                ret = listexproofforb2v(int(arg_list[0]))
        elif pargs.is_matched(opt, ["btchelp"]):
            ret = btchelp()
        elif pargs.is_matched(opt, ["getwalletbalance"]):
            ret = getwalletbalance()
        elif pargs.is_matched(opt, ["getwalletaddressbalance"]):
            if len(arg_list) != 1:
                pargs.exit_error_opt(opt)
            ret = getwalletaddressbalance(arg_list[0])

    logger.debug("end manage.main")

if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
