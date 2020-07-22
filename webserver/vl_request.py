#!/usr/bin/python3
from flask import Flask , url_for, request
from markupsafe import escape
app = Flask(__name__)

import operator
import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import log
import log.logger
import traceback
import datetime
import stmanage
import requests
import comm
import comm.error
import comm.result
import comm.values
from comm.result import result, parse_except
from comm.error import error
from comm.functions import json_reset
from enum import Enum
from vrequest.request_proof import requestproof
from vrequest.request_filter import requestfilter
from btc.btcclient import btcclient
from btc.payload import payload


#module self.name
name="webserver"
logger = log.logger.getLogger(name)
COINS = comm.values.COINS
stmanage.set_conf_env_default()
@app.route('/')
def main():
    args    = request.args
    print(f"args: {args}")
    opt     = args.get("opt")
    opttype = args.get("type")
    state = args.get("state")
    datatype = args.get("datatype", "record")

    if opt is None:
        raise Exception("opt not found.")
    elif opt == "get":
        if datatype == "record":
            return get_record(args)
        elif datatype == "version":
            return get_version(args)
    elif opt == "check":
        return check_record(args)
    elif opt == "set":
        return execute_set(args)
    else:
        raise Exception(f"opt:{opt} not found.")

def execute_set(args):
    opt     = args.get("opt")
    opttype = args.get("type")
    state = args.get("state")
    #btc transaction
    fromaddress     = args.get("fromaddress")
    toaddress       = args.get("toaddress")
    toamount        = float(args.get("toamount"))
    fromprivkeys    = args.get("fromprivkeys")
    combine         = args.get("combine")

    #payload 
    vreceiver       = args.get("vreceiver")
    sequence        = int(args.get("sequence"))
    if fromprivkeys is not None:
        fromprivkeys = json.loads(fromprivkeys)

    if state == "start":
        module          = args.get("module")
        return btc_send_exproof_start(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
                vreceiver, sequence, module)
    elif state in ("end", "mark"):
        version  = int(args.get("version"))
        if state == "end":
            amount   = float(args.get("amount"))
            return btc_send_exproof_end(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
                    vreceiver, sequence, amount, version)
        else:
            return btc_send_exproof_mark(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
                    vreceiver, sequence, toamount, version)
    elif state == "cancel":
        return btc_send_exproof_cancel(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
                vreceiver, sequence)
    elif state == "stop":
        return btc_send_exproof_stop(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
                vreceiver, sequence)
    else:
        raise Exception(f"type:{type} not found.")

def get_b2vswap_type():
    return [item.name.lower() for item in payload.txtype \
            if item.name.lower().startswith("b2v") and item != payload.txtype.B2V]

def get_b2lswap_type():
    return [item.name.lower() for item in payload.txtype \
            if item.name.lower().startswith("b2l")]

def get_bvmap_type():
    return [payload.txtype.B2V.name.lower()]

def get_proof_type():
    types = ["proof"] #get all
    types.extend(get_b2vswap_type())
    types.extend(get_b2lswap_type())
    types.extend(get_bvmap_type())
    return types

def opttype_to_dbname(opttype):
    dbname = ""
    if opttype == "filter":
        return "filter"
    elif opttype in ("mark", "btcmark"):
        return "markproof"
    elif opttype in get_proof_type():
        return "proof"
    elif opttype == "fixtran":
        return "proof"
    else:
        return None 

def list_dbname_for_get_latest_ver():
    dbnames = ["proof", "filter", "mark", "btcmark"]
    return dbnames

def get_version(args):
    opttype = args.get("type")

    if opttype not in list_dbname_for_get_latest_ver():
        raise Exception(f"opttype:{opttype} not found.")

    return get_proof_latest_saved_ver(opttype_to_dbname(opttype))

def get_record(args):
    cursor  = int(args.get("cursor", 0))
    limit   = int(args.get("limit", 10))
    receiver = args.get("address")
    opttype = args.get("type")
    client = get_request_client(opttype_to_dbname(opttype))

    if opttype in get_proof_type():
        state = args.get("state")
        return list_exproof(client, receiver, opttype, state, cursor, limit)
    elif opttype == "fixtran":
        tran_id= args.get("tranid")
        return get_transaction(client, tran_id)
    elif opttype == "filter":
        return list_opreturn_txids(client, cursor, limit)
    elif opttype == "mark":
        return list_proof_mark(client, receiver, cursor, limit)
    elif opttype == "btcmark":
        return list_proof_btcmark(client, receiver, cursor, limit)
    elif opttype in ("balance", "listunspent"):
        minconf = int(args.get("minconf", 1))
        maxconf = int(args.get("maxconf", 99999999))
        if opttype == "listunspent":
            return btc_list_address_unspent(json.loads(receiver), minconf, maxconf)
        else:
            return btc_get_address_balance(receiver, minconf, maxconf)
    else:
        raise Exception(f"type:{type} not found.")

def check_record(args):
    opttype = args.get("type")
    client = get_request_client(opttype_to_dbname(opttype))

    if opttype in get_proof_type():
        address = args.get("address")
        sequence = int(args.get("sequence"))
        state = int(args.get("state"))
        return client.check_proof_is_target_state(address, sequence, state)
    else:
        raise Exception(f"type:{type} not found.")

def get_btcclient():
    return btcclient(name, stmanage.get_btc_conn())

def request_ret(datas):
    return json_reset(datas.to_json())

def btc_get_address_balance(address, minconf = 0, maxconf = 99999999):
    try:
        bclient = get_btcclient()
        ret = bclient.getaddressbalance(address, minconf, maxconf)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def btc_list_address_unspent(address, minconf = 0, maxconf = 99999999):
    try:
        bclient = get_btcclient()
        ret = bclient.listaddressunspent(address, minconf, maxconf)
        if ret.state == error.SUCCEED:
            ret = result(error.SUCCEED, "", ret.datas)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def btc_send_exproof_start(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
        vreceiver, sequence, module):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_start(opttype, vreceiver, sequence, module)
        assert ret.state == error.SUCCEED, f"payload create_ex_start.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)
    
def btc_send_exproof_end(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
        vreceiver, sequence, amount, version):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_end(opttype, vreceiver, sequence, int(amount * COINS), version)
        assert ret.state == error.SUCCEED, f"payload create_ex_end.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def btc_send_exproof_cancel(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
        vreceiver, sequence):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_cancel(opttype, vreceiver, sequence)
        assert ret.state == error.SUCCEED, f"payload create_ex_cancel.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def btc_send_exproof_stop(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
        vreceiver, sequence):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_stop(opttype, vreceiver, sequence)
        assert ret.state == error.SUCCEED, f"payload create_ex_stop.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def btc_send_exproof_mark(opttype, fromaddress, toaddress, toamount, fromprivkeys, combine, \
        vreceiver, sequence, amount, version):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_mark(opttype, vreceiver, sequence, version, int(COINS * amount))
        assert ret.state == error.SUCCEED, f"payload create_ex_mark.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def get_request_client(db):
    if db is None or db == "":
        return None

    if db in ("base"):
        return requestfilter(name, stmanage.get_db(db))
    else:
        return requestproof(name, stmanage.get_db(db))

def get_proof_latest_saved_ver(db):
    try:
        client = get_request_client(db)
        ret = client.get_proof_latest_saved_ver()
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def list_exproof(client, receiver, opttype, state_name, cursor = 0, limit = 10):
    try:
        if state_name is None and receiver is None:
            opttype = None

        ret = client.list_exproof(receiver, opttype, state_name, cursor, limit)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def get_transaction(client, tran_id):
    try:
        ret = client.get_transaction(tran_id)
        print(ret)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def list_proof_mark(client, receiver, cursor = 0, limit = 10):
    try:
        ret = client.list_proof_mark(receiver, cursor, limit)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def list_proof_btcmark(client, receiver, cursor = 0, limit = 10):
    try:
        ret = client.list_proof_btcmark(receiver, cursor, limit)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

def list_opreturn_txids(client, cursor = 0, limit = 10):
    try:
        ret = client.list_opreturn_txids(cursor, limit)
    except Exception as e:
        ret = parse_except(e)
    return request_ret(ret)

'''
with app.test_request_context():
    logger.debug(url_for('tranaddress', chain = "violas", cursor = 0, limit = 10))
    logger.debug(url_for('tranrecord', chain = "violas", sender="af5bd475aafb3e4fe82cf0d6fcb0239b3fe11cef5f9a650e830c2a2b89c8798f", cursor=0, limit=10))
    logger.debug(url_for('trandetail', dtype="v2b", version="5075154"))
'''

if __name__ == "__main__":
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
