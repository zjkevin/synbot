#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

#配置文件工具库
#解析 synbot.ini、cluster_config.yml
#输出到配置文件/group_vars/all、/hosts

import sys
import os
import yaml

from sbc_utils import synbot_conf_utils
from sbc_utils import synbot_group_vars
from sbc_utils import synbot_hosts
from sbc_utils import synbot_tools

import ConfigParser
import re
import codecs
import logging
from fabric.colors import *

SYNBOT_INI = "synbot.ini"
VM_RESOURCE_FILE = "cluster_config/vm_resource.yml"
ZKS_FILE = "zks.yml"
RMS_FILE = "rms.yml"
NNS_FILE = "nns.yml"
JNS_FILE = "jns.yml"


_logger = logging.getLogger(__name__)

#synbot配置实体类
class synbot_env(object):
  """docstring for synbot_env"""
  def __init__(self):
    super(synbot_env, self).__init__()
  #集群的root用户名和密码
  cluster_username = ""
  cluster_passwd = ""
  #集群的配置文件根目录
  cluster_config_path = ""
  cluster_config_file = ""
  #当前集群模块
  cluster_modules = []
  #源
  sources = {"pip_source_address":"",
             "pub_install_pkgs_root":"",
             "cntemplet_url":"",
             "nameserver_ip":"",
             "debian_source_prefix":""
            }
  #模板配置
  imginfo = {"ostemplet_lv_size":"",
             "mount_ostemplet":"",
             "lv_name":"",
             "vg_name":"",
             "current_img":{"file_items":"","os_size":"","unzip_imgs":""}
             }         
  #虚拟机默认配置
  vm_default_vars = {"mem":"",
                     "current_mem":"",
                     "vcpu":""}                 
  #目标机安装目录设定
  appinfo = {"pub_install_apps_root":"",
             "pub_install_log_root":"",
             "pub_temp_root":"",
             "python_cmd":""}

  #集群安装基于hv vm
  base = "hv"
  #synbot设置
  synbot_setting = {"log_mount_auto":"off","tmp_mount_auto":"off"}
  #组件机器组
  app_hosts = {"hadoop_namenode":[],"hadoop_namenode_backup":[],"hadoop_datanode":[],"hadoop_journalnode":[],
               "hadoop_resourcemanager":[],"hadoop_historyjobmanager":[],
               "hbase_master":[],"hbase_regionserver":[],
               "hive":[],"elasticsearch":[],"zookeeper":[],"ntp_server":[]
              }
  os_type = ""

#获取synbot.ini配置文件实体
def get_synbot_ini():
    path = os.path.abspath(".") + "/" + SYNBOT_INI
    if not os.path.exists(path):
      f = open(path,"w")
      f.close()

    def __get_conf_item(sec,k):
      return synbot_conf_utils.get_config_file_item(path,sec,k)

    sbcenv = synbot_env()
    sbcenv.cluster_config_path = __get_conf_item("cluster_config","config_path")
    sbcenv.cluster_config_file = __get_conf_item("cluster_config","config_file")
    #源
    sbcenv.sources = {"pip_source_address":__get_conf_item("sources","pip_source_address"),
                      "pub_install_pkgs_root":__get_conf_item("sources","pub_install_pkgs_root"),
                      "cntemplet_url":__get_conf_item("sources","cntemplet_url"),
                      "nameserver_ip":__get_conf_item("sources","nameserver_ip"),
                      "debian_source_prefix":__get_conf_item("sources","debian_source_prefix")
                      }
    #synbot设置
    sbcenv.synbot_setting = {"log_mount_auto":__get_conf_item("synbot_setting","log_mount_auto"),
                             "tmp_mount_auto":__get_conf_item("synbot_setting","tmp_mount_auto")
                             }
    #模板配置
    current_img = synbot_conf_utils.get_config_file_options(path,"current_img")[0]
    img_items = synbot_conf_utils.get_config_file_options(path,current_img)
    current_img_dict = {}
    for i in img_items:
      current_img_dict[i] = __get_conf_item(current_img,i)
    sbcenv.imginfo = {"ostemplet_lv_size":__get_conf_item("hv","ostemplet_lv_size"),
                      "mount_ostemplet":__get_conf_item("hv","mount_ostemplet"),
                      "lv_name":__get_conf_item("hv","lv_name"),
                      "vg_name":__get_conf_item("hv","vg_name"),
                      "current_img":current_img_dict
                    }

    sbcenv.appinfo = {"pub_install_apps_root":__get_conf_item("app","pub_install_apps_root"),
                      "pub_install_log_root":__get_conf_item("app","pub_install_log_root"),
                      "pub_temp_root":__get_conf_item("app","pub_temp_root"),
                      "python_cmd":__get_conf_item("app","python_cmd")}

    sbcenv.vm_default_vars = {"mem":__get_conf_item("vm_default_vars","mem"),
                              "current_mem":__get_conf_item("vm_default_vars","current_mem"),
                              "vcpu":__get_conf_item("vm_default_vars","vcpu")
                              }

    cluster_modules = synbot_conf_utils.get_config_file_options(path,"cluster_module")
    sbcenv.cluster_modules = cluster_modules

    sbcenv.base = __get_conf_item("cluster_base_on","base")
    sbcenv.cluster_username = __get_conf_item("cluster_user","iuser")
    sbcenv.cluster_passwd = __get_conf_item("cluster_user","ipwd")
    sbcenv.os_type = __get_conf_item("os_type","os")
    parse_synbot_config()
    return sbcenv

#设置配置文件路径
def set_synbot_ini(synbot_env):
    path = os.path.abspath(".") + "/" + SYNBOT_INI
    if not os.path.exists(path):
      f = open(path,"w")
      f.close()
    #修改synbot.ini
    synbot_conf_utils.edit_config_file_item(path,"cluster_config","config_path",synbot_env.cluster_config_path)
    synbot_conf_utils.edit_config_file_item(path,"cluster_config","config_file",synbot_env.cluster_config_file)
    #重新解析synbot配置文件,目的是修改group/all（fabric的配置文件）
    parse_synbot_config()

#解析synbot.ini 修改group/all
def parse_synbot_config():
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(SYNBOT_INI)
    config_all_change_dict = {}
    #img
    if "current_img" not in config.sections():
      print red("missing section 'current_img' in config file %s" % ("/".join(sys.argv[0].split("/")[0:-1]) + "/" + SYNBOT_INI))      
      sys.exit(0)
    current_img = config.options("current_img")

    if not len(current_img) > 0:
      print red("missing options in section 'current_img' please set img info that you want to use")
      sys.exit(0)

    sec_list = ["hv","sources","app","vm_default_vars","cluster_user"]
    sec_list.append(current_img[0])

    def _edit_all_file(config_all_change_dict,current_sec,config):
        if current_sec not in config.sections():
          print red("missing section '%s' in config file %s" % (current_sec,"/".join(sys.argv[0].split("/")[0:-1]) + "/" + SYNBOT_INI))      
          sys.exit(0)
        img_items = config.options(current_sec)
        if not len(img_items) > 0:
          print red("the section '%s' is empty, there is no config been set yet" % current_img)
          sys.exit(0)
        for i in img_items:
           config_all_change_dict[i] = config.get(current_sec,i)
        return config_all_change_dict

    for sec in sec_list:
      config_all_change_dict = _edit_all_file(config_all_change_dict,sec,config)

    config_all_change_dict["current_img"] = current_img[0]
    #修改all文件
    synbot_group_vars.edit_group_vars_all(config_all_change_dict)
    
#根据集群的yaml文件重新生成hosts
#parse synbot.ini
def parse_cluster_yaml_file(base):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(SYNBOT_INI) 
    cluster_config_file = synbot_tools.path_join(config.get("cluster_config","config_path"),base,config.get("cluster_config","config_file"))
    print yellow("parse %s... " % cluster_config_file)
    _logger.info("parse %s... " % cluster_config_file)
    f = open(cluster_config_file,'r')
    cluster_config_yaml = yaml.load(f)
    f.close()
    #创建空的hosts
    f = open("hosts","w")
    f.close()
    #虚拟机列表
    vm_list = []
    #各类app安装所在虚拟机列表
    zk_list = es_list = ntp_servers_list = hbase_master_list = hbase_regionserver_list = hadoop_namenode_list = \
    hadoop_resource_manager_list = hadoop_history_job_manager_list = hadoop_datanode_list = storm_master_list = \
    storm_slave_list = hive_list = spark_list = syndata_list = hadoop_journal_list = hadoop_namenode_backup_list = []
    #虚拟机资源字典
    vm_resource_dict = {}
    #虚拟机磁盘字典
    vm_disk_dict = {}
    sbcenv = get_synbot_ini()
    _logger.info(cluster_config_yaml)

    if cluster_config_yaml.has_key("host_conf") and isinstance(cluster_config_yaml["host_conf"],list):
      host_confs = cluster_config_yaml["host_conf"]
      pre_k = None
      for host_conf in host_confs:
        #上一组机器
        for (k,v) in host_conf.items():
          current_group_vm_list = []
          for host in v["hosts"]:
            if sbcenv.base == "vm":
              current_group_vm_list = current_group_vm_list + synbot_hosts.parse_vm_name(host)
            else:
              current_group_vm_list = current_group_vm_list + synbot_hosts.parse_hv_name(host)
            current_group_vm_list = list(set(current_group_vm_list))
          _logger.info("pre_k:%s" % pre_k)
          _logger.info("current_vm_list:")
          _logger.info(current_group_vm_list)
          if not pre_k == None:
            intersection = [val for val in vm_list if val in current_group_vm_list]
            if len(intersection) > 0:
              print red("host:'%s' already in group:'%s' check your cluster config yaml can not be set to group:'%s'" %(",".join(intersection),pre_k,k))
              sys.exit(0)
          pre_k = k
          vm_list = list(set(vm_list + current_group_vm_list))
          if v.has_key("apps") and isinstance(v["apps"],list):
            for app in v["apps"]:
              if app == "zk":
                zk_list = zk_list + current_group_vm_list
              if app == "ntp_servers":
                print("ntp_servers")
                print(current_group_vm_list)
                ntp_servers_list = ntp_servers_list + current_group_vm_list
                print cyan(ntp_servers_list)
              #hbase
              if app == "hbase_master":
                hbase_master_list = hbase_master_list + current_group_vm_list
              if app == "hbase_regionserver":
                hbase_regionserver_list = hbase_regionserver_list + current_group_vm_list
              #hadoop
              if app == "hadoop_namenode":
                hadoop_namenode_list = hadoop_namenode_list + current_group_vm_list
              if app == "hadoop_namenode_backup":
                hadoop_namenode_backup_list = hadoop_namenode_backup_list + current_group_vm_list
              if app == "hadoop_journal":
                hadoop_journal_list = hadoop_journal_list + current_group_vm_list
              if app == "hadoop_resource_manager":
                hadoop_resource_manager_list = hadoop_resource_manager_list + current_group_vm_list
              if app == "hadoop_history_job_manager":
                hadoop_history_job_manager_list = hadoop_history_job_manager_list + current_group_vm_list              
              if app == "hadoop_datanode":
                hadoop_datanode_list = hadoop_datanode_list + current_group_vm_list              
              if app == "hbase_regionserver":
                hbase_regionserver_list = hbase_regionserver_list + current_group_vm_list
              if app == "es":
                es_list = es_list + current_group_vm_list
              if app == "storm_master":
                storm_master_list = storm_master_list + current_group_vm_list
              if app == "storm_slave":
                storm_slave_list = storm_slave_list + current_group_vm_list
              if app == "hive":
                hive_list = hive_list + current_group_vm_list
              if app == "spark":
                spark_list = spark_list + current_group_vm_list
              if app == "syndata":
                syndata_list = syndata_list + current_group_vm_list
          for vm in current_group_vm_list:
            for mount in v["mounts"]:
              if not vm_disk_dict.has_key(vm):
                vm_disk_dict[vm] = []
              vm_disk_dict[vm].append(mount)
            if sbcenv.base == "vm":
              vm_resource_dict[vm] = {"mem":v["mem"],"current_mem":v["current_mem"],"cpu":v["vcpu"]}          
            else:
              vm_resource_dict[vm] = {"mem":None,"current_mem":None,"cpu":None}
      #check mount
      mount_error = []
      for es_h in es_list:
        es_h_check_result = False
        for mount_info in vm_disk_dict[es_h]:
          if mount_info["name"] == "es":
            es_h_check_result = True
            break
        if not es_h_check_result:
          mount_error.append("%s miss es disk" % es_h)

      for hadoop_name_h in hadoop_namenode_list:
        hadoop_namenode_chk_result = False
        for mount_info in vm_disk_dict[hadoop_name_h]:
          if mount_info["name"] == "nn":
            hadoop_namenode_chk_result = True
            break
        if not hadoop_namenode_chk_result:
          mount_error.append("%s miss hadoop_namenode disk" % hadoop_name_h)      
      
      for hadoop_datanode_h in hadoop_datanode_list:
        hadoop_datanode_chk_result = False
        for mount_info in vm_disk_dict[hadoop_datanode_h]:
          if mount_info["name"] == "dn":
            hadoop_datanode_chk_result = True
            break
        if not hadoop_datanode_chk_result:
          mount_error.append("%s miss hadoop_datanode disk" % hadoop_datanode_h)
      
      for hadoop_journal_h in hadoop_journal_list:
        hadoop_journal_chk_result = False
        for mount_info in vm_disk_dict[hadoop_journal_h]:
          if mount_info["name"] == "jn":
            hadoop_journal_chk_result = True
            break
        if not hadoop_journal_chk_result:
          mount_error.append("%s miss journal_node disk" % hadoop_journal_h)

      for zk_h in zk_list:
        zk_chk_result = False
        for mount_info in vm_disk_dict[zk_h]:
          if mount_info["name"] == "zk":
            zk_chk_result = True
            break
        if not zk_chk_result:
          mount_error.append("%s miss zk disk" % zk_h)
      
      if sbcenv.synbot_setting["log_mount_auto"] == "on":
        for h in vm_list:
          log_chk_result = False
          for mount_info in vm_disk_dict[h]:
            if mount_info["name"] == "log":
              log_chk_result = True
              break
          if not log_chk_result:
            mount_error.append("%s miss log disk" % h)

      if sbcenv.synbot_setting["tmp_mount_auto"] == "on":
        for h in vm_list:
          tmp_chk_result = False
          for mount_info in vm_disk_dict[h]:
            if mount_info["name"] == "tmp":
              tmp_chk_result = True
              break
          if not tmp_chk_result:
            mount_error.append("%s miss tmp disk" % h)
      
      #clear
      for (k,v) in vm_disk_dict.items():
        for i in v:
          if sbcenv.synbot_setting["tmp_mount_auto"] != "on" and i["name"] == "tmp":
            vm_disk_dict[k].remove(i)

      for (k,v) in vm_disk_dict.items():
        for i in v:
          if sbcenv.synbot_setting["log_mount_auto"] != "on" and i["name"] == "log":
            vm_disk_dict[k].remove(i) 

      #{"es":0,"dn":0,"log":0,"tmp":0,"nn":0,"zk":0} 
      if len(mount_error) > 0:
        for e in mount_error:
          print red(e)
        sys.exit(1)
      #vm
      f = open("cluster_config/cluster_disk_config.yml","w")
      cluster_disk_config_yaml = yaml.dump(vm_disk_dict,f)
      _logger.info("dump vm disk config file:cluster_config/cluster_disk_config.yml")
      f.close()
      #mother_land
      if sbcenv.base == "vm":
        synbot_hosts.add_hosts_sec("mother_land",synbot_hosts.get_mother_land(vm_list))
        synbot_hosts.add_hosts_sec("updateimg",synbot_hosts.get_mother_land(vm_list))
      else:
        synbot_hosts.add_hosts_sec("mother_land",vm_list)
        synbot_hosts.add_hosts_sec("updateimg",vm_list)              
      synbot_hosts.add_hosts_sec("installvm",vm_list)
      synbot_hosts.add_hosts_sec("startvm",vm_list)
      synbot_hosts.add_hosts_sec("removevm",vm_list)
      #zk
      synbot_hosts.add_hosts_sec("zookeeper",zk_list)
      #ntp_servers
      synbot_hosts.add_hosts_sec("ntp_servers",ntp_servers_list)
      #ntp_clients
      synbot_hosts.add_hosts_sec("ntp_clients",vm_list)
      #hbase
      synbot_hosts.add_hosts_sec("hbase_master",hbase_master_list)
      synbot_hosts.add_hosts_sec("hbase_regionserver",hbase_regionserver_list)
      synbot_hosts.add_hosts_sec("hbase_zk",zk_list)
      f_zks = open("%s/%s" % (sbcenv.sources["cntemplet_url"],ZKS_FILE),"w")
      f_zks.write("---\n")
      f_zks.write("zks: \n")
      if len(zk_list) > 0:
        for z in zk_list:
          f_zks.write(" - %s:2181\n" % z)
      f_zks.close()
      
      # hbase node relation
      f = open("hosts","a")
      f.write("[hbase:children]\nhbase_master\nhbase_regionserver\n")
      f.close()
      #es
      synbot_hosts.add_hosts_sec("es",es_list)
      #hadoop
      synbot_hosts.add_hosts_sec("hdfs_nn",hadoop_namenode_list)

      f_nns = open("%s/%s" % (sbcenv.sources["cntemplet_url"],NNS_FILE),"w")
      f_nns.write("---\n")
      f_nns.write("nns: \n")
      if len(hadoop_namenode_list) > 0:
        for n in hadoop_namenode_list:
          f_nns.write(" - ns1\n")
      f_nns.close()

      synbot_hosts.add_hosts_sec("hdfs_nb",hadoop_namenode_backup_list)
      f_nns = open("%s/%s" % (sbcenv.sources["cntemplet_url"],NNS_FILE),"a")
      if len(hadoop_namenode_backup_list) > 0:
        for n in hadoop_namenode_backup_list:
          f_nns.write(" - ns2\n")
      f_nns.close()

      synbot_hosts.add_hosts_sec("hdfs_jn",hadoop_journal_list)

      f_jns = open("%s/%s" % (sbcenv.sources["cntemplet_url"],JNS_FILE),"w")
      f_jns.write("---\n")
      f_jns.write("jns: \n")
      if len(hadoop_journal_list) > 0:
        for q in hadoop_journal_list:
          f_jns.write(" - %s:8485\n" % q)
      f_jns.close()

      synbot_hosts.add_hosts_sec("hdfs_rm",hadoop_resource_manager_list)

      f_rms = open("%s/%s" % (sbcenv.sources["cntemplet_url"],RMS_FILE),"w")
      f_rms.write("---\n")
      f_rms.write("rms: \n")
      if len(hadoop_resource_manager_list) > 0:
        __flag = 1
        for r in hadoop_resource_manager_list:
          f_rms.write(" - rm%s\n" % __flag)
          __flag = __flag + 1
      f_rms.close()

      synbot_hosts.add_hosts_sec("hdfs_hm",hadoop_history_job_manager_list)
      synbot_hosts.add_hosts_sec("hdfs_dn",hadoop_datanode_list)
      # hadoop node relation
      f = open("hosts","a")
      f.write("[hdfs_nm:children]\nhdfs_dn\n[hdfs:children]\nhdfs_nn\nhdfs_nb\nhdfs_jn\nhdfs_rm\nhdfs_hm\nhdfs_dn\nhdfs_nm\n")
      f.close()
      #storm
      synbot_hosts.add_hosts_sec("storm_master",storm_master_list)
      synbot_hosts.add_hosts_sec("storm_slave",storm_slave_list)
      # storm node relation
      f = open("hosts","a")
      f.write("[storm:children]\nstorm_master\nstorm_slave\n")
      f.close()
      #hive
      synbot_hosts.add_hosts_sec("hivec",hive_list)
      #spark
      synbot_hosts.add_hosts_sec("sparkc",spark_list)
      #syndata
      synbot_hosts.add_hosts_sec("web_node",syndata_list)
      _logger.info("create /hosts done")
      #edit group_vars/all
      config_all_change_dict = {}
      all_items = ("es_heap_size","hbase_heapsize","spark_executor_memory","esc_name","nodemanager_resource_memory")
      for i in all_items:
        config_all_change_dict[i] = cluster_config_yaml["cluster_app_config"][i]
      synbot_group_vars.edit_group_vars_all(config_all_change_dict)
      sbcenv.app_hosts["hadoop_namenode"] = hadoop_namenode_list
      sbcenv.app_hosts["hadoop_namenode_backup"] = hadoop_namenode_backup_list
      sbcenv.app_hosts["hadoop_datanode"] = hadoop_datanode_list
      sbcenv.app_hosts["hadoop_journalnode"] = hadoop_journal_list
      sbcenv.app_hosts["hadoop_resourcemanager"] = hadoop_resource_manager_list
      sbcenv.app_hosts["hadoop_historyjobmanager"] = hadoop_history_job_manager_list
      sbcenv.app_hosts["hbase_master"] = hbase_master_list
      sbcenv.app_hosts["hbase_regionserver"] = hbase_regionserver_list
      sbcenv.app_hosts["hive"] = hive_list
      sbcenv.app_hosts["elasticsearch"] = es_list
      sbcenv.app_hosts["zookeeper"] = zk_list
      sbcenv.app_hosts["ntp_server"] = ntp_servers_list
      print red(sbcenv.app_hosts)
      chk_cluster_apps_mes = chk_cluster_apps(sbcenv)
      if len(chk_cluster_apps_mes) > 0:
        for c_c_a_m in chk_cluster_apps_mes:
          print red(c_c_a_m)
        print red("use 'sbc -e' to check")
        sys.exit(0)

      #应用内存需求字典
      #app_mem_dict = {}      
      #for h in es_list:
      #  app_mem_dict[h] = "%.2f" % float(cluster_config_yaml["cluster_app_config"]["es_heap_size"].replace("g","").replace("G",""))
      #for h in hbase_regionserver_list:
      #  app_mem_dict[h] = "%.2f" % (float(app_mem_dict[h]) + float(cluster_config_yaml["cluster_app_config"]["hbase_heapsize"].replace("g","").replace("G","")))
      #for h in spark_list:
      #  app_mem_dict[h] = "%.2f" % (float(app_mem_dict[h]) + float(cluster_config_yaml["cluster_app_config"]["spark_executor_memory"].replace("g","").replace("G","")))
      #for h in hadoop_datanode_list:
      #  app_mem_dict[h] = "%.2f" % (float(app_mem_dict[h]) + float(cluster_config_yaml["cluster_app_config"]["nodemanager_resource_memory"])/1024)                   
      ##create VM_RESOURCE_FILE
      #print green(app_mem_dict)
      f = open(VM_RESOURCE_FILE,"w")
      yaml.dump(vm_resource_dict,f)
      _logger.info("dump vm resource file:%s is ok" % VM_RESOURCE_FILE)
      f.close()      

#检查集群的HA组件配置
def chk_cluster_apps(sbcenv):
    error_list = []
    hadoop_install = False
    i_h_nn = len(sbcenv.app_hosts["hadoop_namenode"])
    i_h_nn_b = len(sbcenv.app_hosts["hadoop_namenode_backup"])
    i_h_dn = len(sbcenv.app_hosts["hadoop_datanode"])
    i_h_jn = len(sbcenv.app_hosts["hadoop_journalnode"])
    i_h_rm = len(sbcenv.app_hosts["hadoop_resourcemanager"])
    i_h_hjm = len(sbcenv.app_hosts["hadoop_historyjobmanager"])
    i_hb_hm = len(sbcenv.app_hosts["hbase_master"])
    i_hb_hr = len(sbcenv.app_hosts["hbase_regionserver"])
    i_h = len(sbcenv.app_hosts["hive"])
    i_e = len(sbcenv.app_hosts["elasticsearch"])
    i_z = len(sbcenv.app_hosts["zookeeper"])
    i_n_s = len(sbcenv.app_hosts["ntp_server"])
    if i_n_s < 2:
      error_list.append("ntp servers must be setted 2 hosts or more")
    if (i_h_nn + i_h_nn_b + i_h_dn + i_h_jn + i_h_rm + i_h_hjm) > 0:
      hadoop_install = True
      if not (i_h_nn == 1 and i_h_nn_b == 1):
        error_list.append("hadoop namenode hosts must be 2 for HA, but now is %s" % str(i_h_nn))
      if i_h_dn == 0:
        error_list.append("you miss hadoop datanode hosts setting")
      if i_h_jn < 3 or i_h_jn % 2 == 0:
        error_list.append("hadoop journalnode hosts must be 3 or more than 3 and must be odd number")
      if not i_h_rm == 2:
        error_list.append("hadoop resourcemanager hosts must be 2 for HA")
      if i_h_hjm == 0:
        error_list.append("you miss hadoop historyjobmanager hosts setting")
    if (i_hb_hm + i_hb_hr) > 0:
      if i_hb_hm < 2:
        error_list.append("hbase master must be 2 hosts or more than 2 hosts,but now is %s" % str(i_hb_hm))
      if i_hb_hr == 0:
        error_list.append("you miss hbase regionserver hosts setting")

    if hadoop_install and i_z == 0:
      error_list.append("you miss zookeeper hosts setting")
    if not hadoop_install:
      if i_h > 0:
        error_list.append("you don't install hadoop, hive can't be run")
    if i_z % 2 == 0:
      error_list.append("zookeeper hosts must be odd number")
    return error_list


#检查集群配置文件是否存在
def chk_cluster_yaml_file_exist():
    sbcenv = get_synbot_ini()
    flag = 0
    if sbcenv.cluster_config_file.strip() == "":
      print red("you have not set cluster config file, please set it use:'sbc -d <config_file>'")
      flag = flag + 1
    if sbcenv.cluster_config_path == "":
      print red("you have not set cluster config path, please set it use:'sbc -p <config_file_path>'")
      flag = flag + 1
    if flag == 0:
      return True
    return False

class synbotenv(object):
    """docstring for env"""
    def __init__(self, arg):
        super(env, self).__init__()
        self.arg = arg

    DISK_SYMBOL = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q'\
                  'r','s','t','u','v','w','x','y','z']

    APP_DISK_INDEX = {"es":0,"dn":0,"log":0,"tmp":0,"nn":0,"zk":0,"jn":0}

if __name__ == '__main__':
  get_synbot_ini()

