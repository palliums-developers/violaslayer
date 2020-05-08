#!/bin/bash
#gunicorn -w 4 -b 0.0.0.0:8088 ws_request:app
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
gunicorn -c gunicorn.conf.py vl_request:app
