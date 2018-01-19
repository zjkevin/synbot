#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import time
import logging
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
_logger = logging.getLogger(__name__)

#安装集群
def install_cluster(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    raw_input_config = raw_input(green("the cluster will install depend on config file:%s Y/N " % synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.cluster_config_file)))
    if raw_input_config.lower() not in ("yes","y"):
      sys.exit(0)
    if not __check_sources():
      sys.exit(0)
    __check_hosts()
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    if sbcenv.base == "vm":
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_vm.yml")
    else:
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_hv.yml")
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

#安装集群包含syndata
def install_all_cluster(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    raw_input_config = raw_input(green("the cluster will install depend on config file:%s Y/N " % synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.cluster_config_file)))
    if raw_input_config.lower() not in ("yes","y"):
      sys.exit(0)
    if not __check_sources():
      sys.exit(0)
    __check_hosts()
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    if sbcenv.base == "vm":
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_vm.yml")
    else:
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_hv.yml")
    syndata_install_step = __load_install_steps_config("conf/syndata_prepare.yml")
    install_step = __join_step_list(install_step,syndata_install_step)
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

#重建集群
def rebuild_cluster(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    raw_input_config = raw_input(green("the cluster will rebuild depend on config file:%s Y/N " % synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.cluster_config_file)))
    if raw_input_config.lower() not in ("yes","y"):
      sys.exit(0)
    if not __check_sources():
      sys.exit(0)
    __check_hosts()
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    if sbcenv.base == "vm":
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_vm.yml")
    else:
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_hv.yml")
    stop_cluster_step = __load_install_steps_config("conf/cluster_stop.yml")
    print stop_cluster_step
    install_step = __join_step_list(stop_cluster_step, install_step)
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

#重建集群
def rebuild_all_cluster(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    raw_input_config = raw_input(green("the cluster will rebuild depend on config file:%s Y/N " % synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.cluster_config_file)))
    if raw_input_config.lower() not in ("yes","y"):
      sys.exit(0)
    if not __check_sources():
      sys.exit(0)
    __check_hosts()
    host_list = synbot_hosts.get_hosts_config_sec("installvm")
    if sbcenv.base == "vm":
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_vm.yml")
    else:
      install_step = __load_install_steps_config("conf/cluster_install_steps_depend_hv.yml")
    stop_cluster_step = __load_install_steps_config("conf/cluster_stop.yml")
    install_step = __join_step_list(stop_cluster_step, install_step)
    syndata_install_step = __load_install_steps_config("conf/syndata_prepare.yml")
    install_step = __join_step_list(install_step,syndata_install_step)    
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

def __load_install_steps_config(cluster_install_steps_config_file):
    f = open(cluster_install_steps_config_file)
    d = yaml.load(f)
    print(cyan(d))
    if not d.has_key("install_steps"):
      print(red("cluster_install_steps.yml missing key: \"install_steps\", it must be define")) 
      sys.exit(1)
    return d["install_steps"]

def __check_sources(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    pip_source_address = sbcenv.sources["pip_source_address"]
    pip_source_address_status = synbot_tools.is_open_address(pip_source_address)
    file_items = sbcenv.imginfo["current_img"]["file_items"].split(",")
    cntemplet_url = sbcenv.sources["cntemplet_url"]
    file_status = True
    if sbcenv.base == "vm":
      for item in file_items:
        item = synbot_tools.path_join(cntemplet_url,item)
        if os.path.isfile(item):
          print green("img file: %s is ok" % item)
        else:
          print red("img file: %s is missing" % item)
          file_status = False
    if pip_source_address_status and file_status:
      print green("pip source:%s is ok" % pip_source_address)
      if sbcenv.base == "vm":
        print green("img file is ok")
      return True
    else:
      if pip_source_address_status:
        print green("pip source:%s is ok" % pip_source_address)
      else:
        print red("pip source is down,check it: %s" % pip_source_address)
        _logger.error("pip source is down,check it: %s" % pip_source_address)
      return False

def __join_step_list(list1,list2):
    for i in list1[::-1]:
      list2.insert(0,i)
    return list2

def __check_hosts():
    hosts_file = open("roles/hosts/templates/hosts","r")
    lines = hosts_file.readlines()
    hosts_file.close()
    no_empty_lines = []
    for l in lines:
      if l.strip() not in ("","\n","\t","\r","\r\n"):
        no_empty_lines.append(l.strip())
    if len(no_empty_lines) == 0:
      print red("the hosts is empty, you should use 'sbc -en' to edit network and 'sbc -createhosts' to create it first")
      sys.exit(0)
