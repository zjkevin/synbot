#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import synbot_env

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

#检查zookeeper的磁盘
def zookeeper_disk_check(conf_file):
    pass

#mount zookeeper的磁盘
def zookeeper_disk_mount(conf_file):
    pass

#设置集群配置文件目录
def __set_config_file_path(**arg):
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
        sbcenv.cluster_config_path = path
        #写回配置文件
        synbot_env.set_synbot_ini(sbcenv)
        print green("the config path is been set to: '%s'" % sbcenv.cluster_config_path)
    except Exception, e:
        print red("set config path error:%s" % e)

def zk_install(**arg):
    if len(arg["args"]) == 0:
      os.system("ansible-playbook books/zk/zk_install.yml -e hosts=zookeeper")
    else:
      #修改[zookeeper]组名->[zookeeper_tmp]
      synbot_hosts.rename_hosts_sec("zookeeper","zookeeper_tmp")
      #生成一个临时的zookeeper
      host_list = []
      host_list.extend(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
      host_list.extend(synbot_hosts.parse_vm_name(arg["args"][0].strip()))
      host_list = list(set(host_list))
      synbot_hosts.add_hosts_sec("zookeeper",host_list)
      os.system("ansible-playbook books/zk/zk_install.yml -e hosts=zookeeper")
      #删除[zookeeper]
      synbot_hosts.remove_hosts_sec("zookeeper")
      #修改组名[zookeeper_tmp]->[zookeeper]
      synbot_hosts.rename_hosts_sec("zookeeper_tmp","zookeeper")

    def __check_disk():
      sbcenv = synbot_env.get_synbot_ini()
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
      __disk_yml = synbot_fabric.load_cluster_disk_config_yaml()
      for k in __disk_yml.keys():
        disk_index = 0
        app_disk_index= copy.deepcopy(synbot_fabric.synbotenv.APP_DISK_INDEX)
        disk_index = disk_index + 1
        for item in __disk_yml[k]:
          app_disk_index[item["name"]] = app_disk_index[item["name"]] + 1
  
        os.system("mkdir -p %s/%s" % (sbcenv.sources["cntemplet_url"],k))

      if sbcenv.base == "vm":
        __pv_space_check(disk_space_yaml,"cluster_config/cluster_disk_config.yml")
      else:
        __nude_disk_space_check(disk_space_yaml,"cluster_config/cluster_disk_config.yml")