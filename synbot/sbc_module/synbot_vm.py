#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import shutil

from sbc_utils import synbot_fabric
from sbc_utils import synbot_hosts
from fabric.colors import *

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

#vm初始化
def vm_init(**arg):
    #cp
    shutil.copy("conf/hosts","roles/hosts/templates")
    shutil.copy("conf/hv_soft.yml","roles/hv_soft/tasks/main.yml")
    #执行ansible命令
    #在hosts文件中添加临时组
    if len(arg["args"]) == 0:
      temp_hosts = "installvm"
    else:
      temp_hosts = str(uuid.uuid1())
      synbot_utils._edit_config_file("hosts",temp_hosts,arg["args"][0].split(","))
    os.system("ansible-playbook books/pub/pub_init.yml -e hosts=%s" % temp_hosts)  
    os.system("ansible-playbook books/pub/hosts.yml -e hosts=%s" % temp_hosts)
    os.system("ansible-playbook books/hv/hv_soft.yml -e hosts=%s" % temp_hosts)
    #删除hosts中的随机uuid组
    if not len(arg["args"]) == 0:
      synbot_utils.remove_config_section("hosts",temp_hosts)

#清除虚拟机
def vm_clear(**arg):
    if len(arg["args"]) == 0: 
      print red("you should set which hv you want to clear")
      sys.exit(1)
    else:
      mes_list = synbot_fabric.vm_clear(synbot_hosts.parse_hv_name(arg["args"][0].strip()))
    for l in mes_list:
      print green(l)
