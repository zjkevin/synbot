#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os
import uuid
import synbot_hosts

#在一组机器上执行一个ansible命令
def execmd_on_temphosts(cmd,hosts):
    #在hosts文件中添加临时组
    temp_hosts = str(uuid.uuid1())
    synbot_hosts.add_hosts_sec(temp_hosts,hosts)
    os.system("%s -e hosts=%s" % (cmd,temp_hosts))
    #删除hosts中的随机uuid组
    synbot_hosts.remove_hosts_sec(temp_hosts)

#ssh分发
def ssh_dispense(host_list=None,cluster_pwd='synway'):
    temp_hosts_list = []
    if host_list == None:
      temp_hosts_list = ["mother_land","installvm"]
    else:
      temp_hosts = str(uuid.uuid1())
      synbot_hosts.add_hosts_sec(temp_hosts,host_list)
      temp_hosts_list.append(temp_hosts)
    for h in temp_hosts_list:
        os.system("sshpass -p %s ansible-playbook books/pub/sshkey.yml -e hosts=%s -k" % (cluster_pwd,h))  
    #del hosts uuid group
    if not host_list == None:
      synbot_hosts.remove_hosts_sec(temp_hosts)

def test():
    print("11111")