#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author zhang.jie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from nose.tools import *

import synbot_env

ALL_FILE = "group_vars/all"

SYNBOT_INI_CONTENT = '''
[cluster_config]
config_path = config_path1
config_file = config_file2

[sources]
pub_repo_root = http://www.xxx.s
pip_source_address = http://192.168.50.0:8080
pub_install_pkgs_root = ~/packages1
cntemplet_url = /vm/ostemplet2
nameserver_ip = 192.168.0.1

[hv]
ostemplet_lv_size = 13G
mount_ostemplet = /vm/ostemplet
lv_name = ostemplet
vg_name = vgapp

[app]
pub_install_apps_root = /usr/lib
pub_install_log_root = /var/log
pub_temp_root = /var/syntmp
python_cmd = /usr/bin/python

[cluster_module]
ntp
zk
hadoop
hbase
es
spark
hive
syndata

[current_img]
img

[img]
file_items = vmtemplet.xml,debian71.img.tar.gz
os_size = 11G
unzip_imgs = debian71.img

[vm_default_vars]
mem = 8
current_mem = 8
vcpu = 8

[cluster_base_on]
base = hv
#vm,hv
'''

CLUSTER_CONFIG_FILE='''
---
# virtual machine resource
host_conf:
    - manager1:
        mem: 12
        current_mem: 12
        vcpu: 12
        swap_size: 1G
        mounts:
          - mount:
            name: nn
            disk: /dev/sdc
            size: 100G
        apps:
          - zk
          - ntp_servers
          - hbase_master
          - hadoop_namenode
          - hadoop_resource_manager
          - hadoop_history_job_manager
          - storm_master
          - hive
          - spark
          - es
          - syndata
        hosts: 
         - p1n1
    - manager_backup:
        mem: 12
        current_mem: 12
        vcpu: 12
        swap_size: 1G
        mounts:
          - mount:
            name: nn
            disk: /dev/sdc
            size: 100G
        apps:
          - zk
          - hbase_master
          - hadoop_namenode_backup
          - hadoop_resource_manager
        hosts: 
         - p1n2
    - datanode1:
        mem: 12
        current_mem: 12
        vcpu: 12
        swap_size: 1G
        mounts:
         - mount:
           name: es
           disk: /dev/sdc
           size: 10G
         - mount:
           name: log
           disk: /dev/sdc
           size: 10G
         - mount:
           name: tmp
           disk: /dev/sdc
           size: 10G
        apps:
          - es
          - storm_slave
          - hbase_regionserver
          - hadoop_datanode
          - hadoop_journal
        hosts:
         - "p[1]n[3~6]"
# cluster app config
cluster_app_config:
    es_heap_size: 10g
    hbase_heapsize: 10g
    spark_executor_memory: 10g
    esc_name: es_test
'''

def rename_config_file(old_name,new_name):
    os.rename(old_name,new_name)

def delete_config_file(path):
    os.remove(path)

def create_config_file(content,path):
    f = open(path,"w")
    f.write(content)
    f.close()

def setup():
    old_name = os.path.abspath(".") + "/synbot.ini"
    new_name = os.path.abspath(".") + "/synbot.ini.tmp"
    rename_config_file(old_name,new_name)
    create_config_file(SYNBOT_INI_CONTENT,old_name)
    print('start test synbot_env'.center(80,'*'))

def teardown():
    old_name = os.path.abspath(".") + "/synbot.ini"
    new_name = os.path.abspath(".") + "/synbot.ini.tmp"    
    delete_config_file(old_name)
    rename_config_file(new_name,old_name)    
    print('end test synbot_env'.center(80,'*'))

def check_group_vars_all(item,value):
    f = open(ALL_FILE, 'r')
    lines = f.readlines()
    f.close()
    for l in lines:
      if ":" in l and l.split(":")[0] == item:
        print(":".join(l.split(":")[1:]).strip())
        print(value.strip())
        print("-----------------------------------")
        if ":".join(l.split(":")[1:]).strip() == value.strip():
            return True
        else:
            return False

class TestSynBotENV(object):
    """Test case for synbot_env"""

    def test_get_synbot_ini(self):
        st = synbot_env.get_synbot_ini()
        assert_equal(st.cluster_config_path,"config_path1")
        assert_equal(st.cluster_config_file,"config_file2")
        assert_equal(st.cluster_modules,["ntp","zk","hadoop","hbase","es","spark","hive","syndata"])
        
        assert_equal(st.sources["pub_repo_root"],"http://www.xxx.s")
        assert_equal(st.sources["pip_source_address"],"http://192.168.50.0:8080")
        assert_equal(st.sources["pub_install_pkgs_root"],"~/packages1")
        assert_equal(st.sources["cntemplet_url"],"/vm/ostemplet2")
        assert_equal(st.sources["nameserver_ip"],"192.168.0.1")

        assert_equal(st.imginfo["ostemplet_lv_size"],"13G")
        assert_equal(st.imginfo["mount_ostemplet"],"/vm/ostemplet")
        assert_equal(st.imginfo["lv_name"],"ostemplet")
        assert_equal(st.imginfo["vg_name"],"vgapp")
        assert_equal(st.imginfo["current_img"],{"file_items":"vmtemplet.xml,debian71.img.tar.gz","os_size":"11G","unzip_imgs":"debian71.img"})

        assert_equal(st.vm_default_vars["mem"],"8")
        assert_equal(st.vm_default_vars["current_mem"],"8")
        assert_equal(st.vm_default_vars["vcpu"],"8")
             
        assert_equal(st.appinfo["pub_install_apps_root"],"/usr/lib")
        assert_equal(st.appinfo["pub_install_log_root"],"/var/log")
        assert_equal(st.appinfo["pub_temp_root"],"/var/syntmp")
        assert_equal(st.appinfo["python_cmd"],"/usr/bin/python")          

        assert_equal(st.base,"hv")


    def test_set_synbot_ini(self):
        st = synbot_env.get_synbot_ini()
        st.cluster_config_path = "1"
        st.cluster_config_file = "2"
        synbot_env.set_synbot_ini(st)
        st_check = synbot_env.get_synbot_ini()
        assert_equal(st_check.cluster_config_path,"1")
        assert_equal(st_check.cluster_config_file,"2")

        assert_equal(check_group_vars_all("pub_repo_root","http://www.xxx.s"),True)
        assert_equal(check_group_vars_all("pip_source_address","http://192.168.50.0:8080"),True)
        assert_equal(check_group_vars_all("pub_install_pkgs_root","~/packages1"),True)
        assert_equal(check_group_vars_all("cntemplet_url","/vm/ostemplet2"),True)
        assert_equal(check_group_vars_all("nameserver_ip","192.168.0.1"),True)

        assert_equal(check_group_vars_all("ostemplet_lv_size","13G"),True)
        assert_equal(check_group_vars_all("mount_ostemplet","/vm/ostemplet"),True)
        assert_equal(check_group_vars_all("lv_name","ostemplet"),True)
        assert_equal(check_group_vars_all("vg_name","vgapp"),True)

        assert_equal(check_group_vars_all("pub_install_apps_root","/usr/lib"),True)
        assert_equal(check_group_vars_all("pub_install_log_root","/var/log"),True)
        assert_equal(check_group_vars_all("pub_temp_root","/var/syntmp"),True)
        assert_equal(check_group_vars_all("python_cmd","/usr/bin/python"),True)

        assert_equal(check_group_vars_all("pub_repo_root","http://www.xxx.s"),True)
        assert_equal(check_group_vars_all("pub_repo_root","http://www.xxx.s"),True)
        assert_equal(check_group_vars_all("pub_repo_root","http://www.xxx.s"),True)
        assert_equal(check_group_vars_all("pub_repo_root","http://www.xxx.s"),True)

        assert_equal(check_group_vars_all("file_items","vmtemplet.xml,debian71.img.tar.gz"),True)
        assert_equal(check_group_vars_all("os_size","11G"),True)
        assert_equal(check_group_vars_all("unzip_imgs","debian71.img"),True)

        assert_equal(check_group_vars_all("mem","8"),True)
        assert_equal(check_group_vars_all("current_mem","8"),True)
        assert_equal(check_group_vars_all("vcpu","8"),True)

        assert_equal(check_group_vars_all("current_img","img"),True)