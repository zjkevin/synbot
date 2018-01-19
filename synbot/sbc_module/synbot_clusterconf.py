#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import time
import yaml
import copy
import logging

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from fabric.colors import *
import synbot_env
from sbc_utils import synbot_tools
from sbc_utils import synbot_fabric
from sbc_utils import synbot_hosts

SCAN_PV_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_pv.yml"
SCAN_MEM_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_mem.yml"
SCAN_DISK_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_disk.yml"
CLUSTER_CONF_TEMPLET_HV_FILE = "templates/cluster_config_depend_hv.templet"
CLUSTER_CONF_TEMPLET_VM_FILE = "templates/cluster_config_depend_vm.templet"

_logger = logging.getLogger(__name__)

#创建集群定义文件
def define_cluster_config(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    try:
      if len(arg["args"]) == 0:
        print red("missing config file name, please use 'sbc -d <config_file>' to define it")
        sys.exit(0)
      #非空
      path = arg["args"][0].strip()
      if path == "":
        print red("path must be set")
        sys.exit(0)
      #后缀检查，没有就加
      if path.find(".") == -1:
        path = path + ".yml"
      else:
        if path.split(".")[-1] not in ("yml","yaml"):
          path = path + ".yml"
      if path.split("/")[-1] in (".yml",".yaml"):
        print red("the file must have a name '%s'" % path)
        sys.exit(0)
      #文件
      if path[0] == "/":
        sbcenv.cluster_config_path = synbot_tools.path_join("/".join(path.split("/")[0:-1]))
        sbcenv.cluster_config_file = path.split("/")[-1]
      else:
        if sbcenv.cluster_config_path == "" or sbcenv.cluster_config_path == None:
          sbcenv.cluster_config_path = synbot_tools.path_join("/".join(sys.argv[0].split("/")[0:-1]),"cluster_config")
        else:
          sbcenv.cluster_config_path = synbot_tools.path_join(sbcenv.cluster_config_path,"/".join(path.split("/")[0:-1]))
        sbcenv.cluster_config_file = path.split("/")[-1]
      path = synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.base,sbcenv.cluster_config_file)
      if not os.path.exists(synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.base)):
         os.makedirs(synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.base))
      #exit
      if os.path.exists(path):
        create_validate = raw_input(red("this config file is exit! do you want switch to this config file?(yes/no) or rewrite it(rewrite)"))
        if create_validate.lower() in ("rewrite"):
            create_conf_file_by_templet(sbcenv,path)
            print green("rewrite config file to path:%s success!" % path)       
        elif create_validate.lower() in ("yes","y"):
          print green("switch config file to path:%s success!" % path)
        else:
          sys.exit(0)
      else:
        create_conf_file_by_templet(sbcenv,path)
        print green("create config file to path:%s success!" % path)
      
      #写回配置文件
      sbcenv.cluster_config_path = synbot_tools.path_join("/".join(sbcenv.cluster_config_path.split("/")))
      synbot_env.set_synbot_ini(sbcenv)      
    except Exception, e:
        print red("create config error:%s" % e)

def create_conf_file_by_templet(sbcenv,path):
    __cluster_conf_file = None
    if sbcenv.base == "hv":
      __cluster_conf_file = CLUSTER_CONF_TEMPLET_HV_FILE
    else:
      __cluster_conf_file = CLUSTER_CONF_TEMPLET_VM_FILE
    open(path,"w").write(open(__cluster_conf_file,"r").read())

def edit_config_file(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    conf_file = None
    if sbcenv.cluster_config_path.strip() == "" or sbcenv.cluster_config_file.strip() == "":
      print yellow("warning: please define cluster config file first,you can use 'sbc -d <configname>' to define")
      return True
    if sbcenv.cluster_config_path == "/":
      conf_file = "/%s" % synbot_tools.path_join(sbcenv.base,sbcenv.cluster_config_file)
    else:
      conf_file = synbot_tools.path_join("/".join(sbcenv.cluster_config_path.split("/")),sbcenv.base,sbcenv.cluster_config_file)
    if os.path.exists(conf_file) and os.path.isfile(conf_file):
      #print synbot_tools.path_join("/".join(sbcenv.cluster_config_path.split("/")),sbcenv.base,sbcenv.cluster_config_file)
      os.system("vim %s" % synbot_tools.path_join("/".join(sbcenv.cluster_config_path.split("/")),sbcenv.base,sbcenv.cluster_config_file))
    else:
      print yellow("file: %s is missing or it is a dir not a file check it first, if missing you should define it use 'sbc -d <configname>'" % conf_file)
      return True      
#设置集群配置文件目录
def set_config_file_path(**arg):
    try:
      sbcenv = synbot_env.get_synbot_ini()
      if len(arg["args"]) == 0:
        if sbcenv.cluster_config_path.strip() == "":
          print red("config path has not been set yet, please use 'sbc -p <path>' to set it")
        else:
          print cyan("the config path now is been set to: '%s'" % sbcenv.cluster_config_path)
        if sbcenv.cluster_config_file.strip() == "":
          print red("config file has not been set yet, please use 'sbc -d <config_file>' to define it")
        else:
          if sbcenv.cluster_config_path == "/":
            print cyan("current config file is : '%s%s'" % (sbcenv.cluster_config_path , sbcenv.cluster_config_file))
          else:
            print cyan("current config file is : '%s/%s'" % (sbcenv.cluster_config_path , sbcenv.cluster_config_file))
        sys.exit(0)
      path = arg["args"][0].strip()
      if os.path.isfile(path):
        print red("the path is a file,you must input a dir")
        sys.exit(0)
      else:
        if not os.path.exists(path):
          raw_input_validate = raw_input("this path is not exist do you want to create it?(yes/no)")
          if raw_input_validate.lower() not in ("yes","y"):
            sys.exit(0)
          else:
            os.makedirs(path)
        if path[-1] == "/" and path != "/":
          sbcenv.cluster_config_path = path[0:-1]
        else:
          sbcenv.cluster_config_path = path
        sbcenv.cluster_config_file = ""
        #写回配置文件
        synbot_env.set_synbot_ini(sbcenv)
        print green("the config path is been set to: '%s'" % sbcenv.cluster_config_path)
    except Exception, e:
        print red("set config path error:%s" % e)

#解析synbot.ini、cluster.yml
def parse_cluster_config(**arg):
    #synbot.ini
    synbot_env.parse_synbot_config()
    #cluster.yml
    sbcenv = synbot_env.get_synbot_ini()
    if synbot_env.chk_cluster_yaml_file_exist():
      synbot_env.parse_cluster_yaml_file(sbcenv.base)
    #获取HV的磁盘yml文件
    if sbcenv.base == "vm":
      synbot_fabric.scan_pv()
    else:
      synbot_fabric.scan_disk()
    #检查HV是否足够的磁盘空间分给虚拟机
    if sbcenv.base == "vm":
      f = open(SCAN_PV_FILE,"r")
    else:
      f = open(SCAN_DISK_FILE,"r")
    disk_space_yaml = yaml.load(f)
    f.close()
    # 生成应用磁盘资源表
    __config = synbot_fabric.load_cluster_config(sbcenv.base)
    for k in __config["diskextslist"].keys():
      disk_index = 0
      app_disk_index= copy.deepcopy(synbot_fabric.synbotenv.APP_DISK_INDEX)
      disk_index = disk_index + 1
      for item in __config["diskextslist"][k]:
        app_disk_index[item["name"]] = app_disk_index[item["name"]] + 1

      os.system("mkdir -p %s/%s" % (sbcenv.sources["cntemplet_url"],k))
      f_es = open("%s/%s/es_data_mount.yml" % (sbcenv.sources["cntemplet_url"],k),"w")
      f_es.write("---\n")
      f_es.write("es_data_mount: \n")
      if app_disk_index["es"] > 0:
          for i in range(app_disk_index["es"]):
              f_es.write(" - %s/d%s\n" % ("/var/syndata/es",i+1))
      f_es.close()

      f_hdfs = open("%s/%s/hdfs_data_mount.yml" % (sbcenv.sources["cntemplet_url"],k),"w")
      f_hdfs.write("---\n")
      f_hdfs.write("hdfs_data_mount: \n")
      if app_disk_index["dn"] > 0:
          for i in range(app_disk_index["dn"]):
              f_hdfs.write(" - %s/d%s\n" % ("/var/syndata/dn",i+1))
      f_hdfs.write("hdfs_data_mount_dn: \n")
      if app_disk_index["dn"] > 0:
          for i in range(app_disk_index["dn"]):
              f_hdfs.write(" - %s/d%s/dn\n" % ("/var/syndata/dn",i+1))
      f_hdfs.write("hdfs_data_mount_tmp: \n")
      if app_disk_index["dn"] > 0:
          for i in range(app_disk_index["dn"]):
              f_hdfs.write(" - %s/d%s/tmp\n" % ("/var/syndata/dn",i+1))              
      f_hdfs.close()
    if sbcenv.base == "vm":
      pv_space_check(disk_space_yaml,"cluster_config/cluster_disk_config.yml")
    else:
      nude_disk_space_check(disk_space_yaml,"cluster_config/cluster_disk_config.yml")
    
    #集群内存检查
    synbot_fabric.scan_mem()
    #检查HV是否足够的内存分给应用
    print green("parse cluster config success!")


#基于物理机裸磁盘的容量检查
def nude_disk_space_check(disk_space_yaml,cluster_disk_config_yml):
    f = open(cluster_disk_config_yml,"r")
    cluster_disk_config_yaml = yaml.load(f)
    f.close()

    #一个物理机的同一个分区不能同时分配给两个挂载点
    disk_space_need_dict = {}
    #print green(cluster_disk_config_yaml)
    for (k,v) in cluster_disk_config_yaml.items():
      hv = k
      if not disk_space_need_dict.has_key(hv):
        disk_space_need_dict[hv] = {}
      for m in v:
        if not disk_space_need_dict[hv].has_key(m["disk"]):
          disk_space_need_dict[hv][m["disk"]] = {}
          disk_space_need_dict[hv][m["disk"]]["mount"] = []
          if m.has_key("size"):
            disk_space_need_dict[hv][m["disk"]]["size"] = m["size"]
          else:
            disk_space_need_dict[hv][m["disk"]]["size"] = "0g"
          disk_space_need_dict[hv][m["disk"]]["mount"].append(m["name"])
        else:
          disk_space_need_dict[hv][m["disk"]]["mount"].append(m["name"])
          if m.has_key("size"):
            disk_space_need_dict[hv][m["disk"]]["size"] = synbot_tools.add_space(disk_space_need_dict[hv][m["disk"]]["size"],m["size"])  
          else:
            disk_space_need_dict[hv][m["disk"]]["size"] = "0g"
    disk_error_mes = []
    disk_space_check = {}
    for (k,v) in disk_space_need_dict.items():
      for (i,j) in v.items():
        disk_space_check["%s_%s" % (k,i)] = "fail"
        if len(j["mount"]) > 1:
          disk_error_mes.append("%s on host:%s mount on %s more than one mount point" % (i,','.join(j["mount"]),k))
        if disk_space_yaml.has_key(k):
          if disk_space_yaml[k].has_key(i):
            free_space = float(disk_space_yaml[k][i]["PSize"].replace("g","").replace("G",""))
            needed_space = float(j["size"].replace("g","").replace("G","").split(".")[0])
            if needed_space > free_space:
                disk_error_mes.append("%s is not enough space on %s you need %sG but %sG only" % (i,k,needed_space,free_space))
            disk_space_check["%s_%s" % (k,i)] = "exit"
          else:
            disk_error_mes.append("%s is not exit on host:%s or it is use for os or swap" % (i,k))
        else:
          disk_error_mes.append("there is no disk info on host:%s you may forget execute cmd 'sbc -parse'" % (k))


    for (k,v) in disk_space_check.items():
      if v == "fail":
        disk_error_mes.append("there is not disk %s" % (k))

    if len(disk_error_mes) > 0:
      for err in disk_error_mes:
        print red(err)
        _logger.error(err)
      sys.exit(1)

#基于虚拟机的磁盘容量检查
def pv_space_check(disk_space_yaml,cluster_disk_config_yml):  
    f = open(cluster_disk_config_yml,"r")
    cluster_disk_config_yaml = yaml.load(f)
    f.close()

    #硬盘资源实际需求字典
    disk_space_need_dict = {}
    print green(cluster_disk_config_yaml)
    for (k,v) in cluster_disk_config_yaml.items():
      hv = synbot_hosts.get_hv_name(k)
      if not disk_space_need_dict.has_key(hv):
        disk_space_need_dict[hv] = {}
      for m in v:
        if not disk_space_need_dict[hv].has_key(m["disk"]):
          disk_space_need_dict[hv][m["disk"]] = m["size"]
        else:
          disk_space_need_dict[hv][m["disk"]] = synbot_tools.add_space(disk_space_need_dict[hv][m["disk"]],m["size"])    
    print yellow(disk_space_need_dict)
    disk_error_mes = []
    disk_space_check = {}
    for (k,v) in disk_space_need_dict.items():
      for (i,j) in v.items():
        disk_space_check["%s_%s" % (k,i)] = "fail"
        if disk_space_yaml.has_key(k):
          _logger.info("%s exit" % k)
          for (d_name,d_info) in disk_space_yaml[k].items():
            if i == d_info["PV"]:
              needed_space = int(j.replace("g","").replace("G",""))
              free_space = int(d_info["PFree"].replace("g","").replace("G","").split(".")[0])
              if needed_space > free_space:
                disk_error_mes.append("%s is not enough space for vm on %s you need %sG but %sG only" % (d_info["PV"],k,needed_space,free_space))
              disk_space_check["%s_%s" % (k,i)] = "exit"
        else:
          disk_error_mes.append("there is no host called %s" % k)
          _logger.error("there is no host called %s" % k)
    for (k,v) in disk_space_check.items():
      if v == "fail":
        disk_error_mes.append("there is not disk %s" % (k))

    if len(disk_error_mes) > 0:
      for err in disk_error_mes:
        print red(err)
        _logger.error(err)
      sys.exit(1)

#罗列当前配置文件夹下的配置文件列表
def list_cluster_confs():
    sbcenv = synbot_env.get_synbot_ini()
    if sbcenv.cluster_config_path == "" or sbcenv.cluster_config_path == None:
      sbcenv.cluster_config_path = synbot_tools.path_join("/".join(sys.argv[0].split("/")[0:-1]),"cluster_config",sbcenv.base)
    else:
      sbcenv.cluster_config_path = synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.base,"/".join(path.split("/")[0:-1]))
    print yellow("config files:".center(80,"*"))
    for f in os.listdir(sbcenv.cluster_config_path):
      print yellow(f)

