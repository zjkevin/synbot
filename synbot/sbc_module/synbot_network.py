#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from fabric.colors import *
from sbc_utils import *
from sbc_utils import synbot_ansible
import synbot_env
import yaml
import shutil

_VM_NETWORK_CONF = "conf/network_conf_vm.yml"
_HV_NETWORK_CONF = "conf/network_conf_hv.yml"
_HOSTS_FILE = "roles/hosts/templates/hosts"
_ANSIBLE_CMD_HOSTS = "ansible-playbook books/pub/hosts.yml -e hosts=sendhosts"
_CREATE_HOSTS_FILE = "cluster_config/hosts"
_CLUSTER_IP_FILE = "cluster_config/cluster_ip.yml"

def edit_network_config_file(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    if sbcenv.base == "vm":
      os.system("vim %s" % _VM_NETWORK_CONF)
    else:
      os.system("vim %s" % _HV_NETWORK_CONF)

def ping_host(**arg):
    host_list = []
    if len(arg["args"]) == 0:
      host_list.extend(synbot_hosts.get_hosts_config_sec("mother_land"))
      host_list.extend(synbot_hosts.get_hosts_config_sec("installvm"))
    else:
      host_list.extend(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
      host_list.extend(synbot_hosts.parse_vm_name(arg["args"][0].strip()))
    host_list = list(set(host_list))
    __retry = 1
    if len(arg["args"]) == 2:
      try:
        __retry = int(arg["args"][1].strip())
      except Exception, e:
        print red("retry must be int")
        return False
    synbot_tools.ping_host(host_list,__retry)

def socket_host(**arg):
    #socket_status
    host_list = []
    if len(arg["args"]) == 0:
      host_list.extend(synbot_hosts.get_hosts_config_sec("mother_land"))
      host_list.extend(synbot_hosts.get_hosts_config_sec("installvm"))
    else:
      host_list.extend(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
      host_list.extend(synbot_hosts.parse_vm_name(arg["args"][0].strip()))
    host_list = list(set(host_list))
    __port = 22
    __retry = 1
    if len(arg["args"]) == 2:
      try:
        __port = int(arg["args"][1].strip())
      except Exception, e:
        print red("port must be int")
        return False
    if len(arg["args"]) == 3:
      try:
        __port = int(arg["args"][1].strip())
        __retry = int(arg["args"][2].strip())
      except Exception, e:
        print red("port and retry must be int")
        return False
    synbot_tools.socket_status(host_list,__port,__retry)

def ssh_dispense(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    if len(arg["args"]) == 0:
      synbot_ansible.ssh_dispense(None,sbcenv.cluster_passwd)
    else:
      synbot_ansible.ssh_dispense(synbot_hosts.parse_hv_name(arg["args"][0].strip()),sbcenv.cluster_passwd)

def send_hosts(**arg):
    #二次确认
    hosts_file = open(_HOSTS_FILE,"r")
    lines = hosts_file.readlines()
    hosts_file.close()
    no_empty_lines = []
    for l in lines:
      if l.strip() not in ("","\n","\t","\r","\r\n"):
        no_empty_lines.append(l.strip())
    if len(no_empty_lines) == 0:
      print red("the hosts is empty, you should use 'sbc -en' to edit network and 'sbc -createhosts' to create it first")
      sys.exit(0)
    tmp_lines = []
    l_tmp = ""
    while len(no_empty_lines) > 0:
      if len(no_empty_lines) > 3:
        tmp_lines = no_empty_lines[0:4]
        no_empty_lines = no_empty_lines[4:]
        for l in tmp_lines:
          l_tmp = l_tmp + l.ljust(32," ")
        print green(l_tmp)
      else:
        for l in no_empty_lines:
          l_tmp = l_tmp + l.ljust(32," ")
        print green(l_tmp)
        no_empty_lines = []
      l_tmp = ""
    if "--force" not in arg["args"]:
      raw_input_config = raw_input(green("do you want send this hosts? yes or no(Y\N)"))
      if raw_input_config.lower() not in ("yes","y"):
        sys.exit(0)
    else:
      arg["args"].remove("--force")  
    #执行ansible命令
    #在hosts文件中添加临时组
    host_list = []
    if len(arg["args"]) == 0:
      host_list.extend(synbot_hosts.get_hosts_config_sec("mother_land"))
      host_list.extend(synbot_hosts.get_hosts_config_sec("installvm"))
    else:
      host_list.extend(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
      host_list.extend(synbot_hosts.parse_vm_name(arg["args"][0].strip()))
    host_list = list(set(host_list))
    #生成一个临时的sendhosts
    synbot_hosts.add_hosts_sec("sendhosts",host_list)
    os.system(_ANSIBLE_CMD_HOSTS)
    #删除[mother_land]
    synbot_hosts.remove_hosts_sec("sendhosts")

#创建hosts和集群ip配置yaml
def create_hosts(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    network_conf = None
    if sbcenv.base == "vm":
      network_conf = yaml.load(open(_VM_NETWORK_CONF))  
    else:
      network_conf = yaml.load(open(_HV_NETWORK_CONF))
    
    default_domain = network_conf["default_domain"]
    ipaddress_block = network_conf["ipaddress_block"]
    synbot_tools.create_cluster_ip_yml(ipaddress_block,_CLUSTER_IP_FILE,sbcenv.base)
    print green("%s create success!" % _CLUSTER_IP_FILE)
    synbot_tools.create_hosts(default_domain,ipaddress_block,_CREATE_HOSTS_FILE,sbcenv.base)
    print green("%s create success!" % _CREATE_HOSTS_FILE)
    shutil.copy(_CREATE_HOSTS_FILE,"roles/hosts/templates")
    shutil.copy(_CREATE_HOSTS_FILE,"/etc")