##!/usr/bin/env python
## -*- coding: UTF-8 -*-
##author zhangjie
#
#import os
#import socket
#import sys
#import time
#import datetime
#import yaml
#import re
#import StringIO
#import ConfigParser
#from ConfigParser import SafeConfigParser as __scfgp
#from fabric.colors import *
#import class_vm
#
#_RETRY = 12
#_SLEEP_TIME = 10
#
#def _edit_ansible_hosts_config(config_file,section,configs):
#    config = ConfigParser.ConfigParser(allow_no_value=True)
#    config.read(config_file)
#    config.remove_section(section)
#    config.add_section(section)
#    for c in configs:
#    	config.set(section,c)
#    config.write(open(config_file,"w"))
#
#def _pingvm(host_list):
#    _host_state = []
#    for h in host_list:
#        _host_state.append(0)
#    print all(_host_state)
#    i = 0
#    while i < _RETRY and not all(_host_state):
#        print("listen the vms:") 
#        for h in host_list:
#            ret = os.system("ping -c 1 -W 1 %s &>/dev/null" % h)
#            if ret:
#                _host_state[host_list.index(h)] = 0      
#            else:
#                _host_state[host_list.index(h)] = 1
#        hosts_state_list = {}
#        state_index = 0
#        for h_state in _host_state:
#            hosts_state_list[host_list[state_index]] = h_state
#            state_index = state_index + 1
#        if all(_host_state):
#            print green("success:try(%s)-------%s" %(i,_state_mesage(hosts_state_list)))
#            return True
#        time.sleep(_SLEEP_TIME)
#        i = i + 1
#        #error_mesage = ""
#        print red("error:try(%s)---%s" %(i,_state_mesage(hosts_state_list)))
#    return False
#
#def socket_status(host_list):
#    _host_state = []
#    for h in host_list:
#        _host_state.append(0)
#    print all(_host_state)
#    i = 0
#    while i < _RETRY and not all(_host_state):
#        print("listen the vms:") 
#        for h in host_list:
#            ret = _IsOpen(h,22)
#            if ret:
#                _host_state[host_list.index(h)] = 0      
#            else:
#                _host_state[host_list.index(h)] = 1
#        hosts_state_list = {}
#        state_index = 0
#        for h_state in _host_state:
#            hosts_state_list[host_list[state_index]] = h_state
#            state_index = state_index + 1
#        if all(_host_state):
#            print green("success:try(%s)-------%s" %(i,_state_mesage(hosts_state_list)))
#            return True
#        time.sleep(_SLEEP_TIME)
#        i = i + 1
#        #error_mesage = ""
#        print red("error:try(%s)---%s" %(i,_state_mesage(hosts_state_list)))
#    return False
#
#def _IsOpen(ip,port):
#    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#    s.settimeout(2)
#    try:
#      s.connect((ip,int(port)))
#      s.shutdown(2)
#      print("%d is open" % port)
#      return True
#    except Exception, e:
#      print("%d is down" % port)
#      return False
#
#def _state_mesage(hosts_state_list):
#    mes_list = []
#    for (k,v) in hosts_state_list.items():
#      if v == 1:
#        mes_list.append(green("vm:%s state:on" % k))
#      else:
#        mes_list.append(red("vm:%s state:down!!!" % k))
#    return "|".join(mes_list)
#
## check cluster config file
#def _load_cluster_config(config_file):
#    yml_dict = {}
#    try:
#      yml_file = open(config_file)
#      yml_dict = yaml.load(yml_file)
#    except Exception, e:
#      print(red("config load error:%s" % e))
#      sys.exit(1)
#    if not yml_dict:
#      print(red("it seem that the config file is empty!!!"))
#      sys.exit(1)
#
#    message_list = []
#    check_item = ("hvs","vms","host_conf","cluster_app_config","cluster_data_none_config",\
#      "hosts","ntp_servers","zk","hive","spark","hadoop","es","storm","hbase","syndata")
#    
#    for item in check_item:
#      if item not in yml_dict.keys():
#        message_list.append("'%s' miss in config file which is needed!" % item)
#
#    if len(message_list) > 0:
#      print red("\n".join(message_list))
#      sys.exit(1)
#    
#    _cc_obj = cluster_config()
#    #logic error check
#    f = open("hosts","w")
#    f.close()
#
#    print(cyan(yml_dict["hosts"]))
#
#    # if not yml_dict["hosts"] or not isinstance(yml_dict["hosts"],list):
#    #   print("'hosts' expect to be a list and must be define")
#    #   sys.exit(1)
#    # else:
#    #   for h in yml_dict["hosts"]:
#
#    if not yml_dict["hvs"].has_key("hosts") or not isinstance(yml_dict["hvs"]["hosts"],list):
#      print("hvs hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hvs"]["hosts"])
#      _cc_obj.hv_list = yml_dict["hvs"]["hosts"]
#      _edit_ansible_hosts_config("hosts","mother_land",yml_dict["hvs"]["hosts"])  
#
#    # host list
#    # hosts
#    if not yml_dict["vms"].has_key("hosts") or not isinstance(yml_dict["vms"]["hosts"],list):
#      print("vms hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["vms"]["hosts"])
#      _cc_obj.host_list = yml_dict["vms"]["hosts"]
#      _edit_ansible_hosts_config("hosts","installvm",yml_dict["vms"]["hosts"])	
#      _edit_ansible_hosts_config("hosts","startvm",yml_dict["vms"]["hosts"])
#      _edit_ansible_hosts_config("hosts","removevm",yml_dict["vms"]["hosts"])
#
#    if not yml_dict["ntp_servers"].has_key("hosts") or not isinstance(yml_dict["ntp_servers"]["hosts"],list):
#      print("'ntp_servers' must be define in the cluster")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["ntp_servers"]["hosts"])
#      _edit_ansible_hosts_config("hosts","ntp_servers",yml_dict["ntp_servers"]["hosts"]) 
#
#    if not yml_dict["syndata"].has_key("hosts") or not isinstance(yml_dict["syndata"]["hosts"],list):
#      print("'syndata hosts' must be define in the cluster")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["syndata"]["hosts"])
#      _edit_ansible_hosts_config("hosts","web_node",yml_dict["syndata"]["hosts"]) 
#
#    
#    # es
#    if not yml_dict["es"].has_key("hosts") or not isinstance(yml_dict["es"]["hosts"],list):
#      print("es hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["es"]["hosts"])
#      _cc_obj.es_host_list = yml_dict["es"]["hosts"]
#      _edit_ansible_hosts_config("hosts","es",yml_dict["es"]["hosts"])  
#    
#    # zookeeper
#    if not yml_dict["zk"].has_key("hosts") or not isinstance(yml_dict["zk"]["hosts"],list):
#      print("zk hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["zk"]["hosts"])
#      _cc_obj.zk_host_list = yml_dict["zk"]["hosts"]
#      _edit_ansible_hosts_config("hosts","zookeeper",yml_dict["zk"]["hosts"])
#
#    # hive
#    if not yml_dict["hive"].has_key("hosts") or not isinstance(yml_dict["hive"]["hosts"],list):
#      print("hive hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hive"]["hosts"])
#      _cc_obj.hive_host_list = yml_dict["hive"]["hosts"]
#      _edit_ansible_hosts_config("hosts","hivec",yml_dict["hive"]["hosts"])
#
#    # spark
#    if not yml_dict["spark"].has_key("hosts") or not isinstance(yml_dict["spark"]["hosts"],list):
#      print("spark hosts expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["spark"]["hosts"])
#      _cc_obj.spark_host_list = yml_dict["spark"]["hosts"]
#      _edit_ansible_hosts_config("hosts","sparkc",yml_dict["spark"]["hosts"])   
#
#    #hdfs
#    #name node
#    if not yml_dict["hadoop"]["namenode"] or not isinstance(yml_dict["hadoop"]["namenode"], list):
#      print("hadoop namenode expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hadoop"]["namenode"])
#      _cc_obj.hadoop_namenode = yml_dict["hadoop"]["namenode"]
#      _edit_ansible_hosts_config("hosts","hdfs_nn",yml_dict["hadoop"]["namenode"])       
#
#    #data node
#    if not yml_dict["hadoop"]["datanode"] or not isinstance(yml_dict["hadoop"]["datanode"], list):
#      print("hadoop datanode expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hadoop"]["datanode"])
#      _cc_obj.hadoop_datanode = yml_dict["hadoop"]["datanode"]
#      _edit_ansible_hosts_config("hosts","hdfs_dn",yml_dict["hadoop"]["datanode"])
#
#    #resource manager
#    if not yml_dict["hadoop"]["resource_manager"] or not isinstance(yml_dict["hadoop"]["resource_manager"], list):
#      print("hadoop resource_manager expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hadoop"]["resource_manager"])
#      _cc_obj.hadoop_resource_manager = yml_dict["hadoop"]["resource_manager"]
#      _edit_ansible_hosts_config("hosts","hdfs_rm",yml_dict["hadoop"]["resource_manager"])
#
#    #history job manager
#    if not yml_dict["hadoop"]["history_job_manager"] or not isinstance(yml_dict["hadoop"]["history_job_manager"], list):
#      print("hadoop history_job_manager expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hadoop"]["history_job_manager"])
#      _cc_obj.hadoop_history_job_manager = yml_dict["hadoop"]["history_job_manager"]
#      _edit_ansible_hosts_config("hosts","hdfs_hm",yml_dict["hadoop"]["history_job_manager"])
#
#    # hadoop node relation
#    f = open("hosts","a")
#    f.write("[hdfs_nm:children]\nhdfs_dn\n[hdfs:children]\nhdfs_nn\nhdfs_rm\nhdfs_hm\nhdfs_dn\nhdfs_nm\n")
#    f.close()
#
#    #hbase master
#    print red(yml_dict["hbase"]["master"]["hosts"])
#    if not yml_dict["hbase"]["master"]["hosts"] or not isinstance(yml_dict["hbase"]["master"]["hosts"], list):
#      print("hbase master expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hbase"]["master"]["hosts"])
#      _cc_obj.hbase_master = yml_dict["hbase"]["master"]["hosts"]
#      _edit_ansible_hosts_config("hosts","hbase_master",yml_dict["hbase"]["master"]["hosts"])    
#
#    #hbase hdfs
#    if not yml_dict["hadoop"]["namenode"] or not isinstance(yml_dict["hadoop"]["namenode"], list):
#      print("hadoop namenode expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hadoop"]["namenode"])
#      _edit_ansible_hosts_config("hosts","hbase_hdfs",yml_dict["hadoop"]["namenode"])       
#
#
#    #hbase regionserver
#    if not yml_dict["hbase"]["regionserver"]["hosts"] or not isinstance(yml_dict["hbase"]["regionserver"]["hosts"], list):
#      print("hbase regionserver expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["hbase"]["regionserver"]["hosts"])
#      _cc_obj.hbase_regionserver = yml_dict["hbase"]["regionserver"]["hosts"]
#      _edit_ansible_hosts_config("hosts","hbase_regionserver",yml_dict["hbase"]["regionserver"]["hosts"])   
#
#    #hbase_zk
#    _edit_ansible_hosts_config("hosts","hbase_zk",_cc_obj.zk_host_list)
#
#    # hbase node relation
#    f = open("hosts","a")
#    f.write("[hbase:children]\nhbase_master\nhbase_regionserver\n")
#    f.close()
#
#    # storm master 
#    if not yml_dict["storm"]["master"]["hosts"] or not isinstance(yml_dict["storm"]["master"]["hosts"], list):
#      print("storm master expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["storm"]["master"]["hosts"])
#      _cc_obj.storm_master = yml_dict["storm"]["master"]["hosts"]
#      _edit_ansible_hosts_config("hosts","storm_master",yml_dict["storm"]["master"]["hosts"])
#
#    # storm slave
#    if not yml_dict["storm"]["slave"]["hosts"] or not isinstance(yml_dict["storm"]["slave"]["hosts"], list):
#      print("storm slave expect to be a list")
#      sys.exit(1)
#    else:
#      print cyan(yml_dict["storm"]["slave"]["hosts"])
#      _cc_obj.storm_slave = yml_dict["storm"]["slave"]["hosts"]
#      _edit_ansible_hosts_config("hosts","storm_slave",yml_dict["storm"]["slave"]["hosts"])
#
#    # storm node relation
#    f = open("hosts","a")
#    f.write("[storm:children]\nstorm_master\nstorm_slave\n")
#    f.close()
#    
#    config_all_change_dict = {}
#    if not yml_dict["host_conf"]:
#      print("'host_conf' must be define in 'cluster_config.yml'")
#      sys.exit(1)
#    else:
#      for c in ("mem","swap_size","current_mem","vcpu"):
#        config_all_change_dict[c] = yml_dict["host_conf"][c]
#
#    if not yml_dict["cluster_app_config"]:
#      print("'cluster_app_config' must be define in 'cluster_config.yml'")
#      sys.exit(1)
#    else:
#      for c in ("es_heap_size","hbase_heapsize","spark_executor_memory"):
#        config_all_change_dict[c] = yml_dict["cluster_app_config"][c]
#
#    if not yml_dict["es"].has_key("esc_name"):
#      print("'esc_name' must be define")
#      sys.exit(1)
#    else:
#      _cc_obj.esc_name = yml_dict["es"]["esc_name"]
#      config_all_change_dict["esc_name"] = yml_dict["es"]["esc_name"]
#        
#    #group_vars/all
#    f = open('group_vars/all', 'r')
#    lines = f.readlines()
#    f.close()
#    f = open('group_vars/all', 'w')
#    for l in lines:
#      if ":" in l and l.split(":")[0] in config_all_change_dict.keys():
#        f.write("%s: %s\n" % (l.split(":")[0],config_all_change_dict[l.split(":")[0]]))
#      else:
#        f.write("%s\n" % l.strip())
#    f.close()
#
#    #
#    for h in _cc_obj.host_list:
#      vm = class_vm.VirtualMachine(h)
#      
#    
#    return _cc_obj
#
#def _cmd_execute(install_step_index,step_name,state,cmd,force_continue=0,retry=1):
#    result = False
#    while retry > 0 and not result:
#      retry = retry - 1
#      if not state:
#        if install_step_index > 1:
#          print cyan("do ping!!!!")
#          if not _pingvm(host_list):
#            result = False
#            continue
#        ret = 256
#        print cyan(install_step_item["cmd"])
#        ret = os.system(install_step_item["cmd"])
#        if force_continue and retry < 1:
#          return True
#        if ret:
#          print red("%s fail" % step_name)
#          result = False
#          time.sleep(_SLEEP_TIME)
#          continue
#        else:
#          return True    
#      return True
#    return result 
#
#def _check_disk():
#    result = False
#    f = open("disk_space.tmp","w")
#    f.close()
#    os.system("fab vmpdd.hv_pv_scan")
#    #create disk_space.yml
#    config = ConfigParser.ConfigParser(allow_no_value=True)
#    config.read("disk_space.tmp")
#    data = {}
#    for s in config.sections():
#      data[s] = {}
#      for (k,v) in config.items(s):
#        data[s][k] = {}
#        #/dev/sda6,vgapp,lvm2,a--,455.97g,135.69g
#        items = v.split(",")
#        data[s][k]["PFree"] = _format_disk_size(items[5])
#        data[s][k]["PSize"] = _format_disk_size(items[4])
#        data[s][k]["PV"] = items[0]
#        data[s][k]["VG"] = items[1]
#    f = open("disk_space.yml","w")
#    yaml.dump(data,f)
#    f.close()
#
#def _format_disk_size(size):
#    re_str = "(\d+.*\d*)[G|g]"
#    re_pat = re.compile(re_str)
#    search_ret = re_pat.search(size)
#    blocks = 0
#    if search_ret:
#        blocks = int(float(search_ret.groups()[0]))
#
#    re_str = "(\d+.*\d*)[t|T]"
#    re_pat = re.compile(re_str)
#    search_ret = re_pat.search(size)
#    if search_ret:
#        blocks = float(search_ret.groups()[0])
#        blocks = 1024 * blocks
#    return "%sg" % blocks
#
#def _load_install_steps_config(cluster_install_steps_config_file):
#    f = open(cluster_install_steps_config_file)
#    d = yaml.load(f)
#    print(cyan(d))
#    if not d.has_key("install_steps"):
#      print(red("cluster_install_steps.yml missing key: \"install_steps\", it must be define")) 
#      sys.exit(1)
#    return d["install_steps"]
#
#class cluster_config(object):
#  """docstring for cluster_config"""
#  def __init__(self):
#    super(cluster_config, self).__init__()
#  host_list = []
#  es_host_list = []
#  esc_name = "es_default_name"
#  zk_host_list = []
#  hive_host_list = []
#  spark_host_list = []  
#  hadoop_namenode = []
#  hadoop_datanode = []
#  hadoop_resource_manager = []
#  hadoop_history_job_manager = []
#  hbase_master = []
#  hbase_regionserver = []
#  storm_master = []
#  storm_slave = []  
#  web_node = ""
#  cluster_data_none_config = {}
#
#  vm_list = [] 
#
#if __name__=="__main__":
#   # load
#   # _cc_obj = _load_cluster_config("cluster_config.yml")
#   # _check_disk()
#   # host_list = _cc_obj.host_list
#   # es_host_list = _cc_obj.es_host_list
#   # esc_name = _cc_obj.esc_name
#   # hadoop_namenode = _cc_obj.hadoop_namenode
#   # web_node = "p2n1"
#
#   # install_step = _load_install_steps_config("cluster_install_steps.yml")
#
#   # d0 = datetime.datetime.now()
#   # print green("start time:%s" % d0)
#   # install_step_index = 0
#   # time_list = []
#   # for install_step_item in install_step:
#   #   print cyan(install_step_item)
#   #   print green("index:%s---step_name:%s---state:%s---cmd:%s---force_continue:%s--retry:%s" % (install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"]))
#   #   _cmd_execute(install_step_index,install_step_item["step_name"],install_step_item["state"],install_step_item["cmd"],install_step_item["force_continue"],install_step_item["retry"])
#   #   install_step_index = install_step_index + 1
#   #   time_list.append(datetime.datetime.now())
#   # d1 = datetime.datetime.now()
#   # print green("end time:%s" % d1)
#   # print green("start time:%s end time%s total:%s" % (d0,d1,(d1-d0)))
#   # d_s = d0
#   # d_index = 1
#   # for d in time_list:
#   #   print green("step_%s:%s" % (install_step[d_index-1]["step_name"], (d-d_s)))
#   #   d_s = d
#   #   d_index = d_index + 1



