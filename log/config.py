import logging.config

config = {
   'version': 1,
   'formatters': {
       'simple': {
           #'format': '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
           #'format':'%(asctime)s:%(levelname)s:%(threadName)s:%(thread)d:%(name)s:%(filename)s:%(lineno)d--: ''%(message)s' 
           'format':'%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d--: ''%(message)s' 
           },
       },
   'handlers': {
       'console': {
           'class': 'logging.StreamHandler',
           'level': 'DEBUG',
           'formatter': 'simple'
           },
       'file': {
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': 'bvexchange.log',
           'level': 'DEBUG',
           'formatter': 'simple',
           'backupCount' : 3,
           'maxBytes' : 10000000 #10M
           },
       },
   'loggers':{
       
       'bvelog': {
           'handlers': ['console', 'file'],
           'level': 'DEBUG',
           },
       }
}

