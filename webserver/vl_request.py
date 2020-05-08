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

#module self.name
name="webserver"
logger = log.logger.getLogger(name)

@app.route('/')
def main():
    args    = request.args
    opt     = args.get("opt")
    cursor  = int(args.get("cursor", 0))
    limit   = int(args.get("limit", 10))
    state   = args.get("state")
    receiver= args.get("receiver")

    if opt is None:
        raise Exception("opt not found.")
    if opt == "b2v":
        return list_exproof_state(receiver, state, cursor, limit)
    elif opt == "btcmark":
        return list_btc_mark(receiver, cursor, limit)
    else:
        raise Exception("opt not found.")

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
