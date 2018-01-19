#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from nose.tools import *
from sbc_utils import synbot_tools

class TestSynbotTools(object):

    def test_path_join(self):
        assert_equals(synbot_tools.path_join("/home/hadoop","1111","1.yaml"),"/home/hadoop/1111/1.yaml")
        assert_equals(synbot_tools.path_join("/home/hadoop","/1111","1.yaml"),"/home/hadoop/1111/1.yaml")
        assert_equals(synbot_tools.path_join("/home/hadoop/","/1111/","/1.yaml"),"/home/hadoop/1111/1.yaml")
        assert_equals(synbot_tools.path_join("/home","/1111/","/1.yaml"),"/home/1111/1.yaml")
        assert_equals(synbot_tools.path_join("/home"),"/home")
        assert_equals(synbot_tools.path_join("/"),"/")
        assert_equals(synbot_tools.path_join(""),"")

    def test_format_disk_size(self):
        assert_equals(synbot_tools.format_disk_size("1000G"),"1000g")
        assert_equals(synbot_tools.format_disk_size("1000.1g"),"1000g")
        assert_equals(synbot_tools.format_disk_size("1000GB"),"1000g")
        assert_equals(synbot_tools.format_disk_size("1000.1gb"),"1000g")        
        assert_equals(synbot_tools.format_disk_size("3.2t"),"3276g")

    def test_add_space(self):
        assert_equals(synbot_tools.add_space("1000gb","1g"),"1001g")
        assert_equals(synbot_tools.add_space("1000gb","1GB"),"1001g")
        assert_equals(synbot_tools.add_space("1G","1t"),"1025g")
        assert_equals(synbot_tools.add_space("1GB","1tb"),"1025g")
        assert_equals(synbot_tools.add_space("1gb","1TB"),"1025g")
        assert_equals(synbot_tools.add_space("1t","2t"),"3072g")
        assert_equals(synbot_tools.add_space("1g","1000gb"),"1001g")
        assert_equals(synbot_tools.add_space("1GB","1000gb"),"1001g")
        assert_equals(synbot_tools.add_space("1t","1G"),"1025g")
        assert_equals(synbot_tools.add_space("1tb","1GB"),"1025g")
        assert_equals(synbot_tools.add_space("1TB","1gb"),"1025g")
        assert_equals(synbot_tools.add_space("2t","1t"),"3072g")

_IPADDRESS_INFO_IN1 = {"ipaddress_prefix":"192.168.63",
                  "domain": "dev.s",
                  "netmask": "255.255.255.0",
                  "network": "192.168.63.0",
                  "gateway": "192.168.63.154",
                  "nameserver": "192.168.60.171",
                  "vm_ip": "1~229",
                  "hv_ip": "230~253",
                  "hv_count": [1,2],
                  "vm_count": 5
                 }

_IPADDRESS_INFO_IN2 = {"ipaddress_prefix":"192.168.63",
                  "domain": "dev.s",
                  "netmask": "255.255.255.0",
                  "network": "192.168.63.0",
                  "gateway": "192.168.63.154",
                  "nameserver": "192.168.60.171",
                  "vm_ip": "1~229",
                  "hv_ip": "230~253",
                  "hv_count": [1,2],
                  "vm_count": 5
                 }

class TestCreateIP(object):
    """Test case for create_ip_yml"""

    def test_init_cluster_ip_block(self):
        hosts_list = synbot_tools._init_cluster_ip_block(_IPADDRESS_INFO_IN1,"vm")
        hosts_list_out = [{'ip': '192.168.63.230', 'host': 'poc1', 'type': 'hv'},
                          {'ip': '192.168.63.231', 'host': 'poc2', 'type': 'hv'}, 
                          {'ip': '192.168.63.1', 'host': 'p1n1', 'type': 'vm'}, 
                          {'ip': '192.168.63.2', 'host': 'p1n2', 'type': 'vm'}, 
                          {'ip': '192.168.63.3', 'host': 'p1n3', 'type': 'vm'}, 
                          {'ip': '192.168.63.4', 'host': 'p1n4', 'type': 'vm'}, 
                          {'ip': '192.168.63.5', 'host': 'p1n5', 'type': 'vm'}, 
                          {'ip': '192.168.63.6', 'host': 'p2n1', 'type': 'vm'}, 
                          {'ip': '192.168.63.7', 'host': 'p2n2', 'type': 'vm'}, 
                          {'ip': '192.168.63.8', 'host': 'p2n3', 'type': 'vm'}, 
                          {'ip': '192.168.63.9', 'host': 'p2n4', 'type': 'vm'}, 
                          {'ip': '192.168.63.10', 'host': 'p2n5', 'type': 'vm'}]
        assert_equal(hosts_list,hosts_list_out)
        assert_equal(len(hosts_list),12)
        _IPADDRESS_INFO_IN1["hv_count"] = "253~230"
        hosts_list = synbot_tools._init_cluster_ip_block(_IPADDRESS_INFO_IN2,"vm")