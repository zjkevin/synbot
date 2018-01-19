#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import time
import yaml
import datetime

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from fabric.colors import *
import synbot_env
from sbc_utils import synbot_tools
from sbc_utils import synbot_hosts
_SLEEP_TIME = 10

def restart_cluster(**arg):
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    #es_host_list = _cc_obj.es_host_list
    #esc_name = _cc_obj.esc_name
    #hadoop_namenode = _cc_obj.hadoop_namenode
    #web_node = "p2n1"
    install_step = _load_install_steps_config("conf/cluster_restart.yml")
    d0 = datetime.datetime.now()
    print green("start time:%s" % d0)
    install_step_index = 0
    time_list = []
    for install_step_item in install_step:
      print cyan(install_step_item)
      print green("index:%s---step_name:%s---state:%s---cmd:%s---force_continue:%s--retry:%s" % (install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"]))
      __cmd_execute(host_list,install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"])
      install_step_index = install_step_index + 1
      time_list.append(datetime.datetime.now())
    d1 = datetime.datetime.now()
    print green("end time:%s" % d1)
    print green("start time:%s end time%s total:%s" % (d0,d1,(d1-d0)))
    d_s = d0
    d_index = 1
    for d in time_list:
      print green("step_%s:%s" % (install_step[d_index-1]["step_name"], (d-d_s)))
      d_s = d
      d_index = d_index + 1

def stop_cluster(**arg):
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    #es_host_list = _cc_obj.es_host_list
    #esc_name = _cc_obj.esc_name
    #hadoop_namenode = _cc_obj.hadoop_namenode
    #web_node = "p2n1"
    install_step = _load_install_steps_config("conf/cluster_stop.yml")
    d0 = datetime.datetime.now()
    print green("start time:%s" % d0)
    install_step_index = 0
    time_list = []
    for install_step_item in install_step:
      print cyan(install_step_item)
      print green("index:%s---step_name:%s---state:%s---cmd:%s---force_continue:%s--retry:%s" % (install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"]))
      __cmd_execute(host_list,install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"])
      install_step_index = install_step_index + 1
      time_list.append(datetime.datetime.now())
    d1 = datetime.datetime.now()
    print green("end time:%s" % d1)
    print green("start time:%s end time%s total:%s" % (d0,d1,(d1-d0)))
    d_s = d0
    d_index = 1
    for d in time_list:
      print green("step_%s:%s" % (install_step[d_index-1]["step_name"], (d-d_s)))
      d_s = d
      d_index = d_index + 1

def start_cluster(**arg):
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    #es_host_list = _cc_obj.es_host_list
    #esc_name = _cc_obj.esc_name
    #hadoop_namenode = _cc_obj.hadoop_namenode
    #web_node = "p2n1"
    install_step = _load_install_steps_config("conf/cluster_start.yml")
    d0 = datetime.datetime.now()
    print green("start time:%s" % d0)
    install_step_index = 0
    time_list = []
    for install_step_item in install_step:
      print cyan(install_step_item)
      print green("index:%s---step_name:%s---state:%s---cmd:%s---force_continue:%s--retry:%s" % (install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"]))
      exe_result = __cmd_execute(host_list,install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"])
      if not exe_result:
        print red("step:%s fail, check it" % install_step_item["step_name"])
        sys.exit(0)
      install_step_index = install_step_index + 1
      time_list.append(datetime.datetime.now())
    d1 = datetime.datetime.now()
    print green("end time:%s" % d1)
    print green("start time:%s end time%s total:%s" % (d0,d1,(d1-d0)))
    d_s = d0
    d_index = 1
    for d in time_list:
      print green("step_%s:%s" % (install_step[d_index-1]["step_name"], (d-d_s)))
      d_s = d
      d_index = d_index + 1

def _load_install_steps_config(cluster_install_steps_config_file):
    f = open(cluster_install_steps_config_file)
    d = yaml.load(f)
    if not d.has_key("install_steps"):
      print(red("cluster_install_steps.yml missing key: \"install_steps\", it must be define")) 
      sys.exit(1)
    return d["install_steps"]

def __cmd_execute(host_list,install_step_index,step_name,state,cmd,force_continue=0,retry=1):
    result = False
    while retry > 0 and not result:
      if not state:
        if install_step_index > 1:
          print cyan("ssh connect")
          if not synbot_tools.socket_status(host_list,22,1):
            result = False
            continue
        ret = 256
        print cyan(cmd)
        ret = os.system(cmd)
        retry = retry - 1
        if force_continue and retry < 1:
          return True
        if ret:
          print red("%s fail" % step_name)
          result = False
          time.sleep(_SLEEP_TIME)
          continue
        else:
          return True
      return True
    return result