#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

from sbc_utils import synbot_conf_utils
from fabric.colors import *
import synbot_env

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

#synbot模式设置
def change_mode(mode_flag="hv"):
    sbcenv = synbot_env.get_synbot_ini()
    if sbcenv.base == mode_flag:
      print green("mode already is %s" % sbcenv.base)
    else:
      synbot_conf_utils.edit_config_file_item("synbot.ini", "cluster_base_on", "base", mode_flag)
      synbot_conf_utils.edit_config_file_item("synbot.ini", "cluster_config", "config_path", "")
      synbot_conf_utils.edit_config_file_item("synbot.ini", "cluster_config", "config_file", "")
      print green("set mode %s success" % mode_flag)