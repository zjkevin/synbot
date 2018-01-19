#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os
import sys
import yaml
import ConfigParser
from fabric.colors import *
import synbot_hosts
import synbot_tools
import logging
#fabric的功能封装，提供给sbc使用

_logger = logging.getLogger(__name__)

SCAN_PARTITION_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_partition.tmp"
SCAN_DISK_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_dick.tmp"
SCAN_PV_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_pv.tmp"
SCAN_VM_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_vm.tmp"
SCAN_MEM_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_mem.tmp"
SCAN_PV_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_pv.yml"
SCAN_DISK_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_disk.yml"
SCAN_MEM_FILE = synbot_tools.current_file_directory() + "/../cluster_config/scan_mem.yml" 

SCAN_DISK_CMD = "fab vmpdd.hv_disk_scan"
SCAN_PV_CMD = "fab vmpdd.hv_pv_scan"
MOUNT_DISK_CMD = "fab vmpdd.format_disk_on_hv"
SCAN_VM_CMD = "fab vmpdd.hv_vm_scan"
REMOVE_VM_CMD = "fab vmpdd.vm_remove"
SCAN_MEM_CMD = "fab hardware.hv_mem_scan"


#扫描内存
def scan_mem(host_list=None):
    #message print
    mes_list = []
    #ping mother land
    ping_fail_status = []
    m_ls = []
    if host_list == None:
        m_ls = synbot_hosts.get_hosts_config_sec("mother_land")
    else:
        m_ls = host_list
        #mother_land->mother_land_tmp
        synbot_hosts.rename_hosts_sec("mother_land","mother_land_tmp")
        #mother_land
        synbot_hosts.add_hosts_sec("mother_land",host_list)
    for m_l in m_ls:
      if not synbot_tools.is_open(m_l,22):
        ping_fail_status.append(m_l)
    if len(ping_fail_status) > 0:
      print red("%s can not connect" % ",".join(ping_fail_status))
      _logger.error("%s can not connect" % ",".join(ping_fail_status))
      sys.exit(1)

    f = open(SCAN_MEM_TMP_FILE,"w")
    f.close()
    f = open(SCAN_MEM_FILE,"w")
    f.close()
    os.system(SCAN_MEM_CMD)
    #create disk_space.yml
    f_mem_tmp = open(SCAN_MEM_TMP_FILE,'r')
    f_mem_tmp_dict = yaml.load(f_mem_tmp)
    data = {}
    for (k,v) in f_mem_tmp_dict.items():
        data[k] = v
        mes_list.append("%s memsize:%sG" % (k,v))
    f = open(SCAN_MEM_FILE,"w")
    yaml.dump(data,f)
    f.close()
    if not host_list == None:
        #[mother_land]
        synbot_hosts.remove_hosts_sec("mother_land")
        #mother_land_tmp->mother_land
        synbot_hosts.rename_hosts_sec("mother_land_tmp","mother_land")    
    return mes_list

#扫描硬盘
def scan_disk(host_list=None):
    #message print
    mes_list = []
    #ping mother land
    ping_fail_status = []
    m_ls = []
    if host_list == None:
        m_ls = synbot_hosts.get_hosts_config_sec("mother_land")
    else:
        m_ls = host_list
        #mother_land->mother_land_tmp
        synbot_hosts.rename_hosts_sec("mother_land","mother_land_tmp")
        #mother_land
        synbot_hosts.add_hosts_sec("mother_land",host_list)
    for m_l in m_ls:
      if not synbot_tools.is_open(m_l,22):
        ping_fail_status.append(m_l)
    if len(ping_fail_status) > 0:
      print red("%s can not connect" % ",".join(ping_fail_status))
      _logger.error("%s can not connect" % ",".join(ping_fail_status))
      sys.exit(1)

    f = open(SCAN_PARTITION_TMP_FILE,"w")
    f.close()
    f = open(SCAN_DISK_TMP_FILE,"w")
    f.close()
    os.system(SCAN_DISK_CMD)
    #create disk_space.yml
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(SCAN_PARTITION_TMP_FILE)
    data = {}
    for s in config.sections():
      data[s] = {}
      mes_list.append("%s disk count:%s".center(60,"*") % (s,len(config.items(s))))
      for (k,v) in config.items(s):
        data[s][k] = {}
        #/dev/sda: 500.1 GB, 500107862016 bytes
        #items = v.strip().split(",")
        #data[s][k]["PFree"] = synbot_tools.format_disk_size(items[0].replace("B",""))
        #data[s][k]["PSize"] = synbot_tools.format_disk_size(items[0].replace("B",""))
        data[s][k]["PV"] = k
        data[s][k]["VG"] = None
        data[s][k]["MOUNT"] = None
        mes_list.append("disk:%s size:%s" % (k,v))
    f = open(SCAN_DISK_FILE,"w")
    yaml.dump(data,f)
    f.close()
    if not host_list == None:
        #[mother_land]
        synbot_hosts.remove_hosts_sec("mother_land")
        #mother_land_tmp->mother_land
        synbot_hosts.rename_hosts_sec("mother_land_tmp","mother_land")    
    return mes_list

def scan_pv(host_list=None):
    #message print
    mes_list = []
    #ping mother land
    ping_fail_status = []
    m_ls = []
    if host_list == None:
        m_ls = synbot_hosts.get_hosts_config_sec("mother_land")
    else:
        m_ls = host_list
        #mother_land->mother_land_tmp
        synbot_hosts.rename_hosts_sec("mother_land","mother_land_tmp")
        #mother_land
        synbot_hosts.add_hosts_sec("mother_land",host_list)
    if m_ls == None:
        print red("it seems that the hosts file is empty, please use 'sbc -d <conf_file>' to define it")
        sys.exit(0)
    for m_l in m_ls:
      print green(m_l)
      if not synbot_tools.is_open(m_l,22):
        ping_fail_status.append(m_l)
    if len(ping_fail_status) > 0:
      _logger.error("%s can not connect" % ",".join(ping_fail_status))
      sys.exit(1)

    f = open(SCAN_PV_TMP_FILE,"w")
    f.close()
    os.system(SCAN_PV_CMD)
    #create disk_space.yml
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(SCAN_PV_TMP_FILE)
    data = {}
    for s in config.sections():
      data[s] = {}
      mes_list.append("%s pv count:%s".center(60,"*") % (s,len(config.items(s))))
      for (k,v) in config.items(s):
        data[s][k] = {}
        #/dev/sda6,vgapp,lvm2,a--,455.97g,135.69g
        items = v.split(",")
        data[s][k]["PFree"] = synbot_tools.format_disk_size(items[5])
        data[s][k]["PSize"] = synbot_tools.format_disk_size(items[4])
        data[s][k]["PV"] = items[0]
        data[s][k]["VG"] = items[1]
        mes_list.append("vg:%s pv:%s size:%s free:%s" % (data[s][k]["VG"].ljust(8),data[s][k]["PV"].ljust(10),data[s][k]["PSize"].ljust(10),data[s][k]["PFree"].ljust(10)))
    f = open(SCAN_PV_FILE,"w")
    yaml.dump(data,f)
    f.close()
    if not host_list == None:
        #[mother_land]
        synbot_hosts.remove_hosts_sec("mother_land")
        #mother_land_tmp->mother_land
        synbot_hosts.rename_hosts_sec("mother_land_tmp","mother_land")    
    return mes_list

def vm_clear(host_list=None):
    #message print
    mes_list = []
    #ping mother land
    ping_fail_status = []
    m_ls = []
    if host_list == None:
        m_ls = synbot_hosts.get_hosts_config_sec("mother_land")
    else:
        m_ls = host_list
        #mother_land->mother_land_tmp
        synbot_hosts.rename_hosts_sec("mother_land","mother_land_tmp")
        #mother_land
        synbot_hosts.add_hosts_sec("mother_land",host_list)
    for m_l in m_ls:
      if not synbot_tools.is_open(m_l,22):
        ping_fail_status.append(m_l)
    if len(ping_fail_status) > 0:
      _logger.error("%s can not connect" % ",".join(ping_fail_status))
      sys.exit(1)

    f = open(SCAN_VM_TMP_FILE,"w")
    f.close()
    os.system(SCAN_VM_CMD)
    #create disk_space.yml
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(SCAN_VM_TMP_FILE)
    data = {}
    vm_list = []
    for s in config.sections():
      for (k,v) in config.items(s):
        vm_list.append(k)
    vm_list = list(set(vm_list))        
    if len(vm_list) == 0:
        print cyan("there is no vm on the HV, bye sir!")
    else:
        raw_input_validate = raw_input(red("do you want to remove vm:%s? (yes/no/some)" % ",".join(vm_list)))
        if raw_input_validate.lower() in ("yes","y"):
            synbot_hosts.rename_hosts_sec("removevm","removevm_tmp")
            synbot_hosts.add_hosts_sec("removevm",vm_list)
            os.system(REMOVE_VM_CMD)
            synbot_hosts.remove_hosts_sec("removevm")
            synbot_hosts.rename_hosts_sec("removevm_tmp","removevm")
            print green("vm:%s have been clear!" % ",".join(vm_list))
        elif raw_input_validate.lower() in ("some"):
            some_hosts_str = raw_input(yellow("choose some hosts in :%s" ",".join(vm_list)))
            some_hosts_list = synbot_hosts.parse_vm_name(raw_input_validate.lower())
            synbot_hosts.rename_hosts_sec("removevm","removevm_tmp")
            synbot_hosts.add_hosts_sec("removevm",some_hosts_list&vm_list)
            os.system(REMOVE_VM_CMD)
            synbot_hosts.remove_hosts_sec("removevm")
            synbot_hosts.rename_hosts_sec("removevm_tmp","removevm")                        

    if not host_list == None:
        #[mother_land]
        synbot_hosts.remove_hosts_sec("mother_land")
        #mother_land_tmp->mother_land
        synbot_hosts.rename_hosts_sec("mother_land_tmp","mother_land")    
    return mes_list

def load_cluster_config(base="hv"):
    '''load config file of hostscfg'''
    hostsnetworklist={}
    vg_conf_dict = {}
    hostsiplist={}
    diskextslist={}
    
    f_network_conf = None
    if base == "hv":
        f_network_conf = open('conf/network_conf_hv.yml','r')
    else:
        f_network_conf = open('conf/network_conf_vm.yml','r')
    f_network_conf_dict = yaml.load(f_network_conf)
    for ip_blk in f_network_conf_dict["ipaddress_block"]:
        hostsnetworklist[ip_blk["ipaddress_prefix"]] = '%s.* %s %s %s %s' % (ip_blk["ipaddress_prefix"],ip_blk["netmask"],ip_blk["network"],ip_blk["gateway"],ip_blk["nameserver"])
    f_network_conf.close()

    f_temp = open('cluster_config/cluster_ip.yml','r')
    hostsiplist = yaml.load(f_temp)
    hostsiplist = hostsiplist["ipaddress"]
    f_temp.close()

    f_vg_conf = open('conf/vg_conf.yml','r')
    f_vg_conf_dict = yaml.load(f_vg_conf)
    for (k,v) in f_vg_conf_dict.items():
        vg_conf_dict[k] = v
    f_vg_conf.close()

    config={}
    config.setdefault('hostsnetworklist',hostsnetworklist)
    config.setdefault('vg_conf',vg_conf_dict)  
    config.setdefault('hostsiplist',hostsiplist)
    config.setdefault('diskextslist',load_cluster_disk_config_yaml()) 
    return config

def load_cluster_disk_config_yaml():
    diskextslist = {}
    cluster_disk_config_yaml = None
    if os.path.exists('cluster_config/cluster_disk_config.yml'):
        f = open('cluster_config/cluster_disk_config.yml','r')
        cluster_disk_config_yaml = yaml.load(f)
        f.close()
    if not cluster_disk_config_yaml == None:
        for (k,v) in cluster_disk_config_yaml.items():
            diskextslist.setdefault(k,__disk_config_dict(v))
    return diskextslist

def mount_disk():
    os.system(MOUNT_DISK_CMD)

def __disk_config_dict(config): 
    ret_config = []
    for cfg in config:
        size = ""
        if cfg.has_key("size"):
            if cfg["size"].lower().endswith("g"):
                size = cfg["size"]
            else:
                print red("disk size unit must be 'g', use 'sbc -e' to check")
                sys.exit(0)
        if cfg["name"] in synbotenv.APP_DISK_INDEX.keys():
            vgapp = cfg["vg"] if cfg.has_key("vg") else "vgapp"
            ret_config.append({"name":cfg["name"],"info":{"vg":"%s" % vgapp,"size":"%s" % size,"pvs":"%s" % cfg["disk"]}})
    return ret_config

class synbotenv(object):
    """docstring for env"""
    def __init__(self, arg):
        super(env, self).__init__()
        self.arg = arg

    DISK_SYMBOL = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q'\
                  'r','s','t','u','v','w','x','y','z']

    APP_DISK_INDEX = {"es":0,"dn":0,"log":0,"tmp":0,"nn":0,"zk":0,"jn":0} 

if __name__ == '__main__':
    scan_disk(["poc11"])
    scan_pv(["poc11"])