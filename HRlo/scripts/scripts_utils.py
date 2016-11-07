#!/usr/bin/env python3
import logging
import datetime
import random

class logit(object):


    def __init__(self, name="", **kwargs):

        if kwargs.get('log_file'):
            self.logger = self.get_logger(name, **kwargs)
        else:
            self.logger = None


    def get_logger(self, name="", datefmt="%Y-%m-%d/%H:%M:%S", **config):
    
        time_format = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

        # logger
        logger = logging.getLogger(name+time_format+str(random.random()))
        logger.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(config['log_file'])
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s %(message)s', datefmt=datefmt)
        fh.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
    
        return logger


    def log(self, msg=""):

        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

