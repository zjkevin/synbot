#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os,sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import sbc_utils.synbot_ansible

#在一组机器上执行一个ansible命令
#def test_execmd_on_temphosts(cmd,hosts):
#   synbot_ansible
#
#
#    #在hosts文件中添加临时组
#    temp_hosts = str(uuid.uuid1())
#    synbot_hosts.add_hosts_sec(temp_hosts,hosts)
#    os.system("%s -e hosts=%s" % (cmd,temp_hosts))
#    #删除hosts中的随机uuid组
#    synbot_hosts.remove_hosts_sec(temp_hosts)

#在一组机器上执行ssh分发，默认分发到mother_land和installvm上
#def test_ssh_dispense(host_list=None):
#    temp_hosts_list = []
#    if host_list == None:
#      temp_hosts_list = ["mother_land","installvm"]
#    else:
#      temp_hosts = str(uuid.uuid1())
#      synbot_hosts.add_hosts_sec(temp_hosts,host_list)
#      temp_hosts_list.append(temp_hosts)
#    for h in temp_hosts_list:
#        os.system("sshpass -p synway ansible-playbook books/pub/sshkey.yml -e hosts=%s -k" % h)  
#    #del hosts uuid group
#    if not host_list == None:
#      synbot_hosts.remove_hosts_sec(temp_hosts)

if __name__ == '__main__':
    print sbc_utils.synbot_ansible.test()