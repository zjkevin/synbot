#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from nose.tools import *

import synbot_env

def set():
    if sbcenv == None:
        sbcenv = synbot_env.synbot_env()
    sbcenv.cluster_name = "zhangjie"