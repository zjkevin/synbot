#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author zhang.jie

import json

from nose.tools import *

from tools.create_ip_yml import create_cluster_ip_yml
from tools.create_ip_yml import _init_cluster_ip_block

ipaddress_info_in1 = {"ipaddress_prefix":"192.168.63",
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

ipaddress_info_in2 = {"ipaddress_prefix":"192.168.63",
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
        hosts_list = _init_cluster_ip_block(ipaddress_info_in1)
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
        ipaddress_info_in1["hv_count"] = "253~230"
        hosts_list = _init_cluster_ip_block(ipaddress_info_in1)
        