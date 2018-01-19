# -*- coding: utf-8 -*-

# set environment in this file.

import subprocess as sub

_SYNBOT_DIR = "/home/kevin/synbot_test"

class Conf(object):
    hv_list = ['poc12']
    host_list = ['p12n1','p12n2','p13n3']
    synbot_dir = _SYNBOT_DIR

class Const(object):
    pass


def before_all(context):
    '''init environment.'''
    context.conf = Conf
    context.testmac1 = '192.168.68.17'
    context.testmac2 = '192.168.68.18'
    context.testmac3 = '192.168.68.19'

def after_all(context):
    '''destroy environment.'''
    pass