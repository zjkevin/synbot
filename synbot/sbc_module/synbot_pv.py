#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

#扫描pv
def __scan_pv(**arg):
    if len(arg["args"]) == 0: 
      mes_list = synbot_fabric.scan_pv(None)
    else:
      mes_list = synbot_fabric.scan_pv(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
    for l in mes_list:
      print green(l)
