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
from enum import Enum
from vrequest.request_proof import requestproof
from btc.btcclient import btcclient
from btc.payload import payload


#module self.name
name="webserver"
logger = log.logger.getLogger(name)

@app.route('/')
def main():
    args    = request.args
    opt     = args.get("opt")
    type    = args.get("type")
    receiver= args.get("receiver")

    if opt is None:
        raise Exception("opt not found.")
    if opt == "get":
        cursor  = int(args.get("cursor", 0))
        limit   = int(args.get("limit", 10))

        if type == "b2v":
            state = args.get("state")
            return list_exproof_state(receiver, state, cursor, limit)
        elif typ == "btcmark":
            return list_btc_mark(receiver, cursor, limit)
        elif type == "balance":
            address = args.get("address")
            minconf = args.get("minconf", 1)
            maxconf = args.get("maxconf", 99999999)
            return btc_get_address_balance(address, minconf, maxconf)
        else:
            raise Exception(f"type:{type} not found.")
    elif opt == "set":
        #btc transaction
        fromaddress     = args.get("fromaddress")
        toaddress       = args.get("toaddress")
        toamount        = args.get("toamount")
        fromprivkeys    = args.get("fromprivkeys")
        combine         = args.get("combine")

        #payload 
        vreceiver       = args.get("vreceiver")
        sequence        = args.get("sequence")
        module          = args.get("module")
        version         = args.get("version")
        if type == "start":
            return btc_send_exproof_start(fromaddress, toaddress, toamount, fromprivkeys, combine, \
                    vreceiver, sequence, module)
        elif type == "end":
            return btc_send_exproof_end(fromaddress, toaddress, toamount, fromprivkeys, combine, \
                    vreceiver, sequence, amount, version)
        elif type == "mark":
            return btc_send_exproof_mark(fromaddress, toaddress, toamount, fromprivkeys, combine, \
                    vreceiver, sequence, amount, version)
        else:
            raise Exception(f"type:{type} not found.")
    else:
        raise Exception(f"opt:{opt} not found.")

def get_btcclient():
    return btcclient(name, stmanage.get_btc_conn())

def btc_get_address_balance(address, minconf = 0, maxconf = 99999999):
    try:
        bclient = get_btcclient()
        ret = bclient.getaddressunspent(address, minconf, maxconf)
        if ret.state == error.SUCCEED:
            ret = result(error.SUCCEED, "", ret.datas.get("amountsum"))
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def btc_send_exproof_start(fromaddress, toaddress, toamount, fromprivkeys, combine = None, \
        vreceiver, sequence, module):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_start(vreiceiver, sequence, module)
        assert ret.state == error.SUCCEED, f"payload create_ex_start.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()
    
def btc_send_exproof_end(fromaddress, toaddress, toamount, fromprivkeys, combine = None, \
        vreceiver, sequence, amount, version):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_end(vreiceiver, sequence, amount, version)
        assert ret.state == error.SUCCEED, f"payload create_ex_end.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def btc_send_exproof_mark(fromaddress, toaddress, toamount, fromprivkeys, combine = None, \
        vreceiver, sequence, amount, version):
    try:
        bclient = get_btcclient()
        pl = payload(name)
        ret = pl.create_ex_mark(vreiceiver, sequence, version, amount)
        assert ret.state == error.SUCCEED, f"payload create_ex_mark.{ret.message}"
        data = ret.datas

        ret = bclient.sendtoaddress(fromaddress, toaddress, toamount, fromprivkeys, \
                data = data, combine = combine)
    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

def get_v2bproof_client():
    return requestproof(name, stmanage.get_db("b2vproof"))

def list_exproof_state(receiver, state_name, cursor = 0, limit = 10):
    try:
        client = get_v2bproof_client()
        state = client.proofstate[state_name.upper()]

        if state == client.proofstate.START:
            ret = client.list_exproof_start(receiver, cursor, limit)
        elif state == client.proofstate.END:
            ret = client.list_exproof_end(receiver, cursor, limit)
        else:
            raise Exception(f"state{state} is invalid.")

    except Exception as e:
        ret = parse_except(e)
    return ret.to_json()

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
