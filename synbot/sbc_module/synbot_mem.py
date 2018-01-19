#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

from sbc_utils import synbot_fabric
from fabric.colors import *

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

#扫描内存
def scan_mem(**arg):
    if len(arg["args"]) == 0: 
      mes_list = synbot_fabric.scan_mem(None)
    else:
      mes_list = synbot_fabric.scan_mem(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
    for l in mes_list:
      print green(l)