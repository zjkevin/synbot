#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

import paramiko

PMIKO_LOG = '/var/log/paramiko.log'
SSH_PORT = 22

def paramiko_init(host,username,password): 
  paramiko.util.log_to_file('%s' % PMIKO_LOG)
  ssh = paramiko.SSHClient()
  ssh.load_system_host_keys()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect(host,port=SSH_PORT,username=username,password=password,compress=True)
  return ssh

