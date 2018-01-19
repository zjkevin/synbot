#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import socket
import re
import os
import sys
import inspect
import yaml
import time
import json
import math
from fabric.colors import *

_SLEEP_TIME = 5

#路径拼接
def path_join(*path):
    path_list = []    
    for p in range(0,len(path)):
        path_list = path_list + path[p].strip().split("/")
    path_list_temp = []
    for i in range(0,len(path_list)):
        if path_list[i].strip() == "":
            if i in (0,len(path_list)-1):
                path_list_temp.append(path_list[i])
        else:
            path_list_temp.append(path_list[i])
    if "http://" in path[0]:
        return "/".join(path_list_temp).replace("http:/","http://")
    else:    
        return "/".join(path_list_temp)

#通过IP和端口 监听状态
def is_open(ip,port=80,timeout=2):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
      s.connect((ip,int(port)))
      s.shutdown(timeout)
      return True
    except Exception, e:
      return False

#ping一组主机
def ping_host(host_list,retry=1):
    _host_state = []
    for h in host_list:
        _host_state.append(0)
    i = 0
    while i < retry and not all(_host_state):
        for h in host_list:
            ret = os.system("ping -c 1 -W 1 %s &>/dev/null" % h)
            if ret:
                _host_state[host_list.index(h)] = 0      
            else:
                _host_state[host_list.index(h)] = 1
        hosts_state_list = {}
        state_index = 0
        for h_state in _host_state:
            hosts_state_list[host_list[state_index]] = h_state
            state_index = state_index + 1
        i = i + 1
        if all(_host_state):
            print green("success:try(%s):\n%s" % (i,_state_mesage(hosts_state_list)))
            return True
        time.sleep(_SLEEP_TIME)
        print yellow("error:try(%s):\n%s" %(i,_state_mesage(hosts_state_list)))
    return False

def socket_status(host_list,port=22,retry=1):
    _host_state = []
    for h in host_list:
        _host_state.append(0)
    i = 0
    while i < retry and not all(_host_state):
        for h in host_list:
            ret = is_open(h,port)
            if ret:
                _host_state[host_list.index(h)] = 1      
            else:
                _host_state[host_list.index(h)] = 0
        hosts_state_list = {}
        state_index = 0
        for h_state in _host_state:
            hosts_state_list[host_list[state_index]] = h_state
            state_index = state_index + 1
        i = i + 1    
        if all(_host_state):
            print green("success:try(%s):\n%s" % (i,_state_mesage(hosts_state_list)))
            return True
        time.sleep(_SLEEP_TIME)
        #error_mesage = ""
        print yellow("error:try(%s):\n%s" % (i,_state_mesage(hosts_state_list)))
    return False

#通过http链接，监听状态
def is_open_address(address,timeout=2):
    status = False
    address = address.replace("http://","")
    if ":" in address:
      status = is_open(address.split(":")[0],address.split(":")[1].split('/')[0],timeout)
    else:
      status = is_open(address.split(":")[0],"80",timeout)
    return status

#磁盘空间相加
def add_space(size1,size2):
    s1,s2 = 0,0
    size1 = size1.lower().replace("b","")
    size2 = size2.lower().replace("b","")
    if "t" in str(size1):
        s1 = int(size1[0:-1]) * 1024
    elif "g" in str(size1):
        s1 = size1[0:-1] 
    if "t" in str(size2):
        s2 = int(size2[0:-1]) * 1024 
    elif "g" in str(size2):
        s2 = size2[0:-1]
    return str(int(s1)+int(s2)) + "g"

#格式化磁盘大小，统一出输入为g
def format_disk_size(size):
    size = size.lower().replace("b","")
    re_str = "(\d+.*\d*)[g]"
    re_pat = re.compile(re_str)
    search_ret = re_pat.search(size)
    blocks = 0
    if search_ret:
        blocks = int(float(search_ret.groups()[0]))
    re_str = "(\d+.*\d*)[t]"
    re_pat = re.compile(re_str)
    search_ret = re_pat.search(size)
    if search_ret:
        blocks = float(search_ret.groups()[0])
        blocks = 1024 * blocks
    return "%sg" % int(blocks)

def _init_cluster_ip_block(ipaddress_info,base):
    try:
        ips = range(1,256)
        if base == "vm":
            for k in ("hv_ip","vm_ip","hv_count","vm_count","ipaddress_prefix"):
                if not ipaddress_info.has_key(k):
                    print red("%s must be set in conf file,but missing!" % k)
                    sys.exit(1)
        if base == "hv":
            for k in ("hv_ip","hv_count","ipaddress_prefix"):
                if not ipaddress_info.has_key(k):
                    print red("%s must be set in conf file,but missing!" % k)
                    sys.exit(1)        
                
        ipaddress_prefix = ipaddress_info["ipaddress_prefix"]
        if "~" not in ipaddress_info["hv_ip"]:
            print red("hv_ip:%s is wrong, must like this:[<int>~<int>]" % ipaddress_info["hv_ip"])
            print red("use sbc command:sbc -en to check")
            sys.exit(1)
        hv_start = ipaddress_info["hv_ip"].split("~")[0]
        hv_end = ipaddress_info["hv_ip"].split("~")[1]
    
        vm_start = 0
        vm_end = 0
        vm_count_every_hv = 0
    
        if base == "vm":
            if "~" not in ipaddress_info["vm_ip"]:
                print red("vm_ip:%s is wrong, must like this:[<int>~<int>]" % ipaddress_info["vm_ip"])
                print red("use sbc command:sbc -en to check")
                sys.exit(1)
            vm_start = ipaddress_info["vm_ip"].split("~")[0]
            vm_end = ipaddress_info["vm_ip"].split("~")[1]
            vm_count_every_hv = ipaddress_info["vm_count"]

        pocs = ipaddress_info["hv_count"]
        if not isinstance(pocs,list):
            print red("hv_count must be a list like this [1,5] means poc1,poc2,poc3,poc4,poc5")
            sys.exit(1)
        else:
            if len(pocs) != 2:
                print red("hv_count must be a list like this [1,5] length must be 2, but [1] or [1,3,4,...] is wrong")
                print red("use sbc command:sbc -en to check")
                sys.exit(1)               
        for i in [{"hv_ip@<int>~<int>":hv_start},
                  {"hv_ip@<int>~<int>":hv_end},
                  {"vm_ip@<int>~<int>":vm_start},
                  {"vm_ip@<int>~<int>":vm_end},
                  {"vm_count@<int>":vm_count_every_hv},
                  {"hv_count@[<int>,<int>]":pocs[0]},
                  {"hv_count@[<int>,<int>]":pocs[1]}]:
            inf = i.keys()[0].split("@")
            try:
                int(i.values()[0])
            except Exception, e:
                print red("'%s' type must be like this:%s" % (inf[0],inf[1]))
                print red("use sbc command:sbc -en to check")
                sys.exit(1) 
        
        if int(pocs[0]) > int(pocs[1]):
            print red("hv_count:%s is wrong, left is big than right" % pocs)
            print red("use sbc command:sbc -en to check")
            sys.exit(1)
        #hv
        host_ip_list = [] 
        hv_index = 0
        for i in range(int(pocs[0]),int(pocs[1])+1):
            ip = int(hv_start) + hv_index
            hv_index = hv_index + 1
            if ip > int(hv_end):
                print red("there is not enough ip address for the hv 'poc%s' use ip:%s.%s!!!" % (i,ipaddress_prefix,ip))
                sys.exit(1)
            if not ip in ips:
                print red("the ip:%s is not exist or it is used for other host alread!!!")
                sys.exit(1)
            else:
                host_ip_list.append({"host":"poc%s" % i,"ip":"%s.%s" % (ipaddress_prefix,ip),"type":"hv"})
                ips.remove(ip)
    
        #vm
        vm_index = 1    
        for i in range(pocs[0],pocs[1]+1):
            for j in range(1,vm_count_every_hv+1):
                ip = int(vm_start) + j + int(vm_count_every_hv)*(vm_index -1) - 1
                if ip > int(vm_end):
                     print("there is not enough ip address when give ip to vm:p%sn%s: %s.%s!!!" % (i,j,ipaddress_prefix,ip))
                     sys.exit(1)
                if not ip in ips:
                     print("the ip:%s is not exist or it is used for other host alread!!!")
                     sys.exit(1)
                host_ip_list.append({"host":"p%sn%s" % (i,j),"ip":"%s.%s" % (ipaddress_prefix,ip),"type":"vm"})               
                ips.remove(ip)
            vm_index = vm_index + 1
        return host_ip_list
    except Exception, e:
        raise e

#创建集群的ip配置yaml cluster_config/cluster_ip.yml
def create_cluster_ip_yml(ipaddress_block,cluster_ip_file,base):
    host_ip_list = []
    f = open(cluster_ip_file,"w")
    f.write("---\n")
    f.write("name: the ipaddress for cluster\n")
    f.write("domain: dev.s\n")    
    for ipaddress_info in ipaddress_block:
        host_ip_list = host_ip_list + _init_cluster_ip_block(ipaddress_info,base)
        f.write("%s: \n" % ipaddress_info["ipaddress_prefix"])
        f.write("  netmask: %s\n" % ipaddress_info["netmask"])
        f.write("  network: %s\n" % ipaddress_info["network"])
        f.write("  gateway: %s\n" % ipaddress_info["gateway"])
        f.write("  nameserver: %s\n" % ipaddress_info["nameserver"])
        f.write("  domain: %s\n" % ipaddress_info["domain"])
    f.write("ipaddress: \n")
    __check_host_repetition(host_ip_list)
    for h in host_ip_list:
        f.write("  %s: %s\n" % (h["host"],h["ip"]))     
    f.close()

#创建集群自定义hosts cluster_config/hosts
def create_hosts(default_domain,ipaddress_block,create_hosts_file,base):
    host_ip_list = []
    f = open(create_hosts_file,"w")
    f.write("127.0.0.1 localhost\n\n")    
    for ipaddress_info in ipaddress_block:
        host_ip_list = _init_cluster_ip_block(ipaddress_info,base)
        domain = ipaddress_info["domain"] if ipaddress_info["domain"].strip() != "" else default_domain   
        __check_host_repetition(host_ip_list)
        for h in host_ip_list:
            #__update_etc_hosts("%s %s\n" % (h["ip"],h["host"]))
            f.write("%s %s\n" % (h["ip"],h["host"]))
        for h in host_ip_list:
            #__update_etc_hosts("%s %s.%s\n" % (h["ip"],h["host"],domain))
            f.write("%s %s.%s\n" % (h["ip"],h["host"],domain))
        host_ip_list = []        
    f.close()

#检查host_ip_list是否有重复
def __check_host_repetition(host_ip_list):
    check_dict = {}
    repeat_host = {}
    for h in host_ip_list:
        if not check_dict.has_key(h["host"]):
            check_dict[h["host"]] = 1
        else:
            check_dict[h["host"]] = check_dict[h["host"]] + 1
    for (k,v) in check_dict.items():
        if v > 1:
            repeat_host[k] = v
    if len(repeat_host) > 0:
        for (k,v) in repeat_host.items():
            print red("%s repeat: %s times" % (k,v))
        print red("use sbc command:sbc -en to check")
        sys.exit(1)

#更新本机的/etc/hosts文件
def __update_etc_hosts(host_line):
    hosts_file = open("/etc/hosts","r")
    lines = hosts_file.readlines()
    hosts_file.close()
    line_exist = False
    for l in lines:
        if len(l.strip().split(" ")) == 2:
            print(l.strip())
            print(host_line.strip())
            if l.strip() == host_line.strip():
                line_exist = True
    if not line_exist:
        hosts_file = open("/etc/hosts","a+")
        hosts_file.write(host_line)
        hosts_file.close()

# function: get directory of current script, if script is built
#  into an executable file, get directory of the excutable file
def current_file_directory():
    path = os.path.realpath(sys.path[0])
    if os.path.isfile(path):
        path = os.path.dirname(path)
        return os.path.abspath(path)
    else:
        caller_file = inspect.stack()[1][1]
        return os.path.abspath(os.path.dirname(caller_file))   

#主机信息状态输出
def _state_mesage(hosts_state_list):
    mes_list = []
    for (k,v) in hosts_state_list.items():
      if v == 1:
        mes_list.append(green("vm:%s state:on" % k))
      else:
        mes_list.append(yellow("vm:%s state:down!!!" % k))
    return "\n".join(mes_list)

#json->dict
def json_to_dict(json_str):
    try:
        return json.JSONDecoder().decode(json_str)
    except Exception, e:
        raise e

#string newline
def str_newline(long_str,size,indent):
    start_index = 0
    end_index = size
    str_list = []
    while long_str[start_index:end_index]:
        str_list.append("%s%s" % (" "*indent , long_str[start_index:end_index]))
        start_index = start_index + size
        end_index = end_index + size
    return "\n".join(str_list)

#dict->json
def dict_to_json(d):
    try:
        return json.JSONEncoder().encode(d)
    except Exception, e:
        raise e

if __name__ == '__main__':
    #__update_etc_hosts(["192.168.50.40 poc1000"])
    #print is_open("192.168.60.172")
    #print is_open("192.168.60.172","80")
    #print is_open("192.168.60.172",22)
    #print is_open_address("http://tsp.apps.s")
    json_str = '{"name1":"zhangjie","age":32}'
    d = json_to_dict(json_str)
    print type(d)
    print dict_to_json(d)

