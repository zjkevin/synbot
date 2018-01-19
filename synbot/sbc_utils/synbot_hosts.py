#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

import os
import synbot_conf_utils
import synbot_tools
import re

HOSTS_FILE = synbot_tools.current_file_directory() + "/../hosts"

#从hosts文件中得到一个节
def get_hosts_config_sec(section):
    return synbot_conf_utils.get_config_file_options(HOSTS_FILE,section)

#更改节点名称
def rename_hosts_sec(section_oldname,section_newname):
    synbot_conf_utils.rename_config_section(HOSTS_FILE,section_oldname,section_newname)

#新增一个节点
def add_hosts_sec(section_name,value):
    synbot_conf_utils.edit_config_file(HOSTS_FILE,section_name,value)

#删除一个节点
def remove_hosts_sec(section_name):
    synbot_conf_utils.remove_config_section(HOSTS_FILE,section_name)

#输入一组虚拟机列表 得到物理机列表
def get_mother_land(vm_list):
    mother_land_list = []
    for h in vm_list:
      mother_land_list.append(get_hv_name(h))
    mother_land_list = list(set(mother_land_list))
    return mother_land_list

#输入一个虚拟机名称，得到一个hv名称 p1n2->poc1
def get_hv_name(vm_name):
    #pxny get x
    pattern = re.compile(r'([A-Za-z]+)(\d+)([A-Za-z]+)(\d+)')
    for m in pattern.finditer(vm_name):
        return "poc" + m.groups()[1]
    return "None"    

def parse_vm_name(name_strs):
    host_str_list = []
    host_list = []
    def __pattern_finder(pattern,host_str_list):
      for m in pattern.finditer(name_strs):
        host_str_list.append(m.groups())
      return host_str_list
    #p1n1
    pattern = re.compile(r'([A-Za-z]+)(\d+)([A-Za-z]+)(\d+)')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p[1~9]n[1~9]
    pattern = re.compile(r'([A-Za-z]+)(\[\d+~\d+\])([A-Za-z]+)(\[\d+~\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p1n[1~9]
    pattern = re.compile(r'([A-Za-z]+)(\d+)([A-Za-z]+)(\[\d+~\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p1n[9]
    pattern = re.compile(r'([A-Za-z]+)(\d+)([A-Za-z]+)(\[\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p[1]n1
    pattern = re.compile(r'([A-Za-z]+)(\[\d+\])([A-Za-z]+)(\d+)')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p[1]n[1]
    pattern = re.compile(r'([A-Za-z]+)(\[\d+\])([A-Za-z]+)(\[\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #p[1]n[1~9]
    pattern = re.compile(r'([A-Za-z]+)(\[\d+\])([A-Za-z]+)(\[\d+~\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)    
    #p[1~9]n[1]
    pattern = re.compile(r'([A-Za-z]+)(\[\d+~\d+\])([A-Za-z]+)(\d+)')
    host_str_list = __pattern_finder(pattern,host_str_list)
    
    def __compute_start_end(str_c):
        if "[" in str_c:
          if "~" in str_c:
            start_c = str_c.replace("[","").replace("]","").split("~")[0]
            end_c = str_c.replace("[","").replace("]","").split("~")[1]
          else:
            start_c = str_c.replace("[","").replace("]","")         
            end_c = str_c.replace("[","").replace("]","")
        else:
          start_c = str_c
          end_c = str_c
        if int(start_c) > int(end_c):
          return (None,None)
        return (start_c,end_c)

    for strs in host_str_list:
      start_h = 0
      end_h = 0
      start_v = 0
      end_v = 0
      start_v, end_v = __compute_start_end(strs[3])
      start_h, end_h = __compute_start_end(strs[1])
      if start_h == None or end_h == None or start_v == None or end_v == None:
        continue
      for i in range(int(start_h),int(end_h)+1):
        for j in range(int(start_v),int(end_v)+1):
          host_list.append("%s%s%s%s" % (strs[0],i,strs[2],j))   
    return host_list

def parse_hv_name(name_strs):
    host_str_list = []
    host_list = []
    def __pattern_finder(pattern,host_str_list):
      for m in pattern.finditer(name_strs):
        host_str_list.append(m.groups())
      return host_str_list
    #poc1
    pattern = re.compile(r'(poc{1})(\d+)')
    host_str_list = __pattern_finder(pattern,host_str_list)
    #poc[1~9]
    pattern = re.compile(r'(poc{1})(\[\d+~\d+\])')
    host_str_list = __pattern_finder(pattern,host_str_list)
    def __compute_start_end(str_c):
        if "[" in str_c:
          if "~" in str_c:
            start_c = str_c.replace("[","").replace("]","").split("~")[0]
            end_c = str_c.replace("[","").replace("]","").split("~")[1]
          else:
            start_c = str_c.replace("[","").replace("]","")         
            end_c = str_c.replace("[","").replace("]","")
        else:
          start_c = str_c
          end_c = str_c
        if int(start_c) > int(end_c):
          return (None,None)
        return (start_c,end_c)
    for strs in host_str_list:
      start_h = 0
      end_h = 0
      start_h, end_h = __compute_start_end(strs[1])
      if start_h == None or end_h == None:
        continue
      for i in range(int(start_h),int(end_h)+1):
        #for j in range(int(start_v),int(end_v)+1):
        host_list.append("poc%s" % i)
    host_list = list(set(host_list))    
    return host_list 

if __name__ == '__main__':
    #print get_hosts_config_sec("mother_land")
    #print get_hv_name("p1n3")
    #print get_mother_land(["p1n2","p1n3","p2n1","p3n1"])
    #print parse_vm_name("p[11~1]n1,p[12~8]n[7~5],p1n[11~1],p1n1")
    #print parse_hv_name("poc1,poc[2~8],poc[10~19],poc[4~7]")
    print parse_hv_name("poc1,poc[2~8],p[11~1]n1,p[12~8]n[7~5],poc[4~7]")
    print parse_vm_name("poc1,poc[2~8],p[1~11]n1,p[12~8]n[7~5],poc[4~7]")