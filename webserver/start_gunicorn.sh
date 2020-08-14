#!/bin/bash
#gunicorn -w 4 -b 127.0.0.1:8066 ws_request:app
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
gunicorn -c gunicorn.conf.py vl_request:app
