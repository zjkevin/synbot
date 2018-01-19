#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from fabric.api import env, run, execute, put, sudo, settings, task , cd
import datetime

@task
def dfc(hosts=None, huser="hadoop", pwd="hadoop"):
    '''get free disk on cluster 
Arguments:
    hosts: host list,sample hosts={host1,host2,host3} ， hosts=host1
    huser:  username
    pwd:  password'''
    env.user=huser
    env.password=pwd
    env.hosts=hosts
    run("df -k $HDATA_HOME")
