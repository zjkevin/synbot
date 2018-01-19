#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import yaml
import copy

from sbc_utils import synbot_fabric
from fabric.colors import *

import synbot_env
from sbc_utils import synbot_tools
from sbc_utils import synbot_fabric
from sbc_utils import synbot_hosts

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

SCAN_PV_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_pv.yml"
SCAN_DISK_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_disk.yml"
CLUSTER_DISK_CONFIG = synbot_tools.current_file_directory() + "/../cluster_config/cluster_disk_config.yml"

#扫描磁盘
def scan_disk(**arg):
    if len(arg["args"]) == 0: 
      mes_list = synbot_fabric.scan_disk(None)
    else:
      mes_list = synbot_fabric.scan_disk(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
    for l in mes_list:
      print green(l)

#格式化磁盘
def format_disk(**arg):
    #synbot.ini
    synbot_env.parse_synbot_config()
    #cluster.yml
    sbcenv = synbot_env.get_synbot_ini()
    if synbot_env.chk_cluster_yaml_file_exist():
      synbot_env.parse_cluster_yaml_file(sbcenv.base)
    else:
        sys.exit(0)
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
    #集群内存检查
    #synbot_fabric.scan_mem()
    #检查HV是否足够的内存分给应用
    __dict_hosts_disk = {}
    print green("format disk done!")
    for k,v in disk_space_yaml.items():
      print yellow(k.center(80,"*"))
      __vk_list = []
      for vk,vv in v.items():
        __vk_list.append(vk)
      __vk_list.sort()
      if not __dict_hosts_disk.has_key("|".join(__vk_list)):
        __dict_hosts_disk["|".join(__vk_list)] = [k]
      else:
        __dict_hosts_disk["|".join(__vk_list)].append(k)
      print green(" ".join(__vk_list))
    print yellow("collect infomation".center(80,"*"))
    for k,v in __dict_hosts_disk.items():
      print yellow("|".join(v))
      print green(" ".join(k.split("|")))
        

def mount_disk(**arg):
    f = open(CLUSTER_DISK_CONFIG,'r')
    cluster_disk_config_dict = yaml.load(f)
    f.close()
    #disk_config_list = cluster_disk_config_dict[host_name]
    #app_disk_index = copy.deepcopy(synbot_fabric.synbotenv.APP_DISK_INDEX)
    #for d_c in disk_config_list:
    #    #- {disk: /dev/sda5, mount: null, name: nn, size: 10G}
    #    app_disk_index[d_c["name"]] = app_disk_index[d_c["name"]] + 1
    #    run("sed -i '/%s/'d /etc/fstab" % d_c["disk"])
    #    run("mount -a")
    #    run("mkfs.ext4 %s" % d_c["disk"])
    #    if d_c["name"] == "log":
    #        run("sed -i '$a %s /var/%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"]))
    #    elif d_c["name"] == "tmp":
    #        run("sed -i '$a %s /%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"]))
    #    elif d_c["name"] == "dn":
    #        run("sed -i '$a %s /var/syndata/%s/d%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"],app_disk_index[d_c["name"]]))
    #        run("mkdir -p /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
    #        run("mkdir -p /var/syndata/%s/d%s/dn" % (d_c["name"],app_disk_index[d_c["name"]]))
    #        run("mkdir -p /var/syndata/%s/d%s/tmp" % (d_c["name"],app_disk_index[d_c["name"]]))
    #        run("chown -R hadoop:hadoop /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
    #    else:
    #        run("sed -i '$a %s /var/syndata/%s/d%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"],app_disk_index[d_c["name"]]))
    #        run("mkdir -p /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
    #        run("chown -R hadoop:hadoop /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
    #    run("mount -a")
    synbot_fabric.mount_disk()
    print green("mount disk success!")