#!/bin/bash 

export FLASK_APP=vl_request.py
export FLASK_ENV=development
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
flask run -h 127.0.0.1 -p 8066
