# config.py
import os

import multiprocessing

debug     = True
loglevel    = 'debug'
bind        = "0.0.0.0:8066"
pidfile     = "log/gunicorn.pid"
accesslog   = "log/access.log"
errorlog    = "log/debug.log"
daemon      = False

workers = multiprocessing.cpu_count()
x_forwarded_for_header = 'X-FORWARDED-FOR'
