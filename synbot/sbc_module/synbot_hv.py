#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
from sbc_utils import synbot_hosts
import synbot_env
import shutil

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

CONF_HOSTS = "cluster_config/hosts"

#hv初始化
#根据集群方案基于虚拟机还是物理机选择不同的初始化方案
def hv_init(**arg):
    if not os.path.exists(CONF_HOSTS):
      print red("%s is missing please execute 'sbc -en' to edit network config then execute 'sbc -hosts' to create" % CONF_HOSTS)
      sys.exit(1)
    shutil.copy(CONF_HOSTS,"roles/hosts/templates")
    sbcenv = synbot_env.get_synbot_ini()
    _hv_soft_file = ""
    if sbcenv.base == "vm":
      _hv_soft_file = "soft_base_on_vm.yml"
    else:
      _hv_soft_file = "soft_base_on_hv.yml"
    print(_hv_soft_file)
    shutil.copy("conf/%s" % _hv_soft_file,"roles/hv_soft/tasks/main.yml")
    def __do_someaction():
        os.system("ansible-playbook books/pub/pub_init.yml -e hosts=mother_land")  
        os.system("ansible-playbook books/hv/hv_soft.yml -e hosts=mother_land")
        if sbcenv.base == "vm":
          os.system("fab vmpdd.network_interfaces_edit")
        
    #执行ansible命令
    #在hosts文件中添加临时组
    if len(arg["args"]) == 0:
      __do_someaction()
    else:
      #修改[mother_land]组名->[mother_land_tmp]
      synbot_hosts.rename_hosts_sec("mother_land","mother_land_tmp")
      #生成一个临时的mother_land
      synbot_hosts.add_hosts_sec("mother_land",synbot_hosts.parse_hv_name(arg["args"][0].strip()))
      __do_someaction()
      #删除[mother_land]
      synbot_hosts.remove_hosts_sec("mother_land")
      #修改组名[mother_land_tmp]->[mother_land]
      synbot_hosts.rename_hosts_sec("mother_land_tmp","mother_land")

#分发文件到服务器上
def update_img_for_hv(**arg):
    if len(arg["args"]) == 0:
      os.system("fab vmpdd.hv_prepareimg")
    else:
      #修改[updateimg]组名->[updateimg_tmp]
      synbot_hosts.rename_hosts_sec("updateimg","updateimg_tmp")
      #生成一个临时的updateimg
      synbot_hosts.add_hosts_sec("updateimg",arg["args"][0].split(","))
      os.system("fab vmpdd.hv_prepareimg")
      #删除[updateimg]
      synbot_hosts.remove_hosts_sec("updateimg")
      #修改组名[updateimg_tmp]->[updateimg]
      synbot_hosts.rename_hosts_sec("updateimg_tmp","updateimg")
