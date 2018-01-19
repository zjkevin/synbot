#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from nose.tools import *
from sbc_utils import synbot_hosts

class TestSynbotHosts(object):

    def test_path_join(self):
        pass