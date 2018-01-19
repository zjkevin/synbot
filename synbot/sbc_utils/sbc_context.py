#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import sys

sys.path.append('..')
import synbot_env

class SbcContext(object):
    """docstring for SbcContext"""
    def __init__(self, arg):
        super(SbcContext, self).__init__()
        self.arg = arg
    sbt_env = None
    cluster_config = None

def set_sbt_env(sbt_env):
    SbcContext.sbt_env = sbt_env

def get_sbt_env():
    return SbcContext.sbt_env

def set_cluster_config(cluster_config):
    SbcContext.cluster_config = cluster_config

def get_cluster_config():
    return SbcContext.cluster_config

def get_config_files():
    return {"HELP_MENU_FILE":"conf/help_menu.yml",\
            "1":"2"}




