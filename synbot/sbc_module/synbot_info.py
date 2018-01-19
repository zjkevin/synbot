#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys
import yaml
import urllib2
import codecs
import logging
import logging.config

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from fabric.colors import *
import synbot_env
from sbc_utils import synbot_tools
from sbc_utils import sbc_context

_DEBIAN_SOURCE_DIR_FILE = synbot_tools.current_file_directory() + "/../conf/debian_source_directory.yml"

with codecs.open('./conf/logging.yaml', 'r', 'utf-8') as logging_file:
  logging.config.dictConfig(yaml.load(logging_file))

_logger = logging.getLogger(__name__)


#CN节点配置检查，查看是否符合系统运行的规范
def get_cn_info(**arg):
    success_mes_list = []
    error_mes_list = []
    
    #需要检查的文件列表
    chk_file_dict = [{"file":"/root/.ssh/config",\
                      "error_mes":"the ssh config file '/root/.ssh/config' is missing",\
                      "help":"create this file and write two lines: 'StrictHostKeyChecking no' 'UserKnownHostsFile /dev/null' and restart ssh", \
                      "success_mes":"the ssh config file '/root/.ssh/config' is ok"},
                      {"file":"/root/.ssh/id_rsa",\
                      "error_mes":"the ssh id_rsa file '/root/.ssh/id_rsa' is missing",\
                      "help":"ssh-keygen -C 'my synbot root key'", \
                      "success_mes":"the ssh id_rsa file '/root/.ssh/id_rsa.pub' is ok"},
                      {"file":"/root/.ssh/id_rsa.pub",\
                      "error_mes":"the ssh id_rsa.pub file '/root/.ssh/id_rsa.pub' is missing",\
                      "help":"ssh-keygen -C 'my synbot root key'", \
                      "success_mes":"the ssh id_rsa.pub file '/root/.ssh/id_rsa.pub' is ok"}]

    sbcenv = sbc_context.get_sbt_env()
    #检查镜像文件
    if sbcenv.base == "vm":
      for f in sbcenv.imginfo["current_img"]["file_items"].split(","):
        img_file = synbot_tools.path_join(sbcenv.sources["cntemplet_url"],f)
        chk_file_dict.append({"file":img_file,\
                              "error_mes":"this file:'%s' is missing" % img_file,\
                              "help":"check the folder:'%s' on the CN" % sbcenv.sources["cntemplet_url"],\
                              "success_mes":"the img file:'%s' is ok" % img_file
                            })
    def __chk_file():
        for f in chk_file_dict:
          if not os.path.exists(f["file"]):
            error_mes_list.append({"mes":f["error_mes"],"help":f["help"]})
          else:
            success_mes_list.append({"mes":f["success_mes"]})

    __chk_file()
    
    #检查用户，synbot以root权限使用
    if os.geteuid() != 0:
      error_mes_list.append({"mes":"cn must run as root","help":"use use:root"})
    else:
      success_mes_list.append({"mes":"the user is root","help":""})
    
    #检查软件
    pip_pack_list = {}
    command = "pip freeze"
    r = os.popen(command)
    info = r.readlines()
    for line in info:
      if len(line.strip().split("=="))==2:
        p = line.strip().split("==")[0]
        v = line.strip().split("==")[1]
        pip_pack_list[p.lower()] = v

    for items in ("fabric","ansible"):
      if items not in pip_pack_list.keys():
        error_mes_list.append({"mes":"package %s is missing","help":"pip install %s" (items.capitalize(),items)})
      else:
        success_mes_list.append({"mes":"package '%s' is ok version:%s" % (items.capitalize(),pip_pack_list[items])})
    
    #检查debian源
    with open(_DEBIAN_SOURCE_DIR_FILE,'rb') as f:
      d = yaml.load(f)
      for x in d["dir"]:
        try:
          address = synbot_tools.path_join(sbcenv.sources["debian_source_prefix"],x)
          f = urllib2.urlopen(address)
          if f.code == 200:
            success_mes_list.append({"mes":"debian source address:%s is online" % address,"help":"check synbot.ini for debian_source_prefix"})
          else:
            error_mes_list.append({"mes":"debian source address:%s is offline" % address,"help":"check synbot.ini for debian_source_prefix"}) 
        except Exception, e:
          error_mes_list.append({"mes":"debian source address:%s is offline" % address,"help":"check synbot.ini for debian_source_prefix"}) 
   
    try:
      pip_source_address = sbcenv.sources["pip_source_address"].strip()
      f = urllib2.urlopen(pip_source_address)
      if f.code == 200:
        success_mes_list.append({"mes":"pip source address:%s is online" % pip_source_address,"help":"check synbot.ini for pip_source_address"})
      else:
        error_mes_list.append({"mes":"pip source address:%s is offline" % pip_source_address,"help":"check synbot.ini for pip_source_address"})           
    except Exception, e:
      error_mes_list.append({"mes":"pip source address:%s is offline" % pip_source_address,"help":"check synbot.ini for pip_source_address"})   
              
    #address = "http://192.168.50.31:8080"
    #if synbot_tools.is_open_address(address):
    #  success_mes_list.append({"mes":"debian source address:%s is online" % address,"help":"check synbot.ini for debian_source_prefix"})
    #else:
    #  error_mes_list.append({"mes":"debian source address:%s is offline" % address,"help":"check synbot.ini for debian_source_prefix"})       
    #信息输出
    if len(error_mes_list) > 0:
      print red("error:")
      for l in error_mes_list:
        print red(l["mes"])+" "+yellow(l["help"])
    if len(success_mes_list) > 0:
      print green("success:")
      for l in success_mes_list:
        print green(l["mes"])

#检查源状态
def check_sources(**arg):
    sbcenv = synbot_env.get_synbot_ini()
    pip_source_address = sbcenv.sources["pip_source_address"]
    pip_source_address_status = synbot_tools.is_open_address(pip_source_address)
    file_items = sbcenv.imginfo["current_img"]["file_items"].split(",")
    cntemplet_url = sbcenv.sources["cntemplet_url"]
    file_status = True
    if sbcenv.base == "vm":
      for item in file_items:
        item = synbot_tools.path_join(cntemplet_url,item)
        if os.path.isfile(item):
          print green("img file: %s is ok" % item)
        else:
          print red("img file: %s is missing" % item)
          file_status = False
    if pip_source_address_status and file_status:
      print green("pip source:%s is ok" % pip_source_address)
      if sbcenv.base == "vm":
        print green("img file is ok")
      return True
    else:
      if pip_source_address_status:
        print green("pip source:%s is ok" % pip_source_address)
      else:
        print red("pip source is down,check it: %s" % pip_source_address)
        _logger.error("pip source is down,check it: %s" % pip_source_address)
      return False