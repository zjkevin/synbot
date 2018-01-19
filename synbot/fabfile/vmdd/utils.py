#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, settings,hide
import re

def lvexist(lvname,vg):
    with settings(warn_only=True),hide("output"):
        rst = run("lvs -a --units B %s |awk 'NR>1{print $1,$4}'" % vg)
        rlines = [line.strip().split(" ") for line in rst.split('\n')]
        for line in rlines:
            if line[0] == lvname:
                return True
        return False    

def vminfo(vmname):
	with settings(warn_only=True),hide("output"):
		rst = run("virsh list --all")
		
		rlines = [line.strip() for line in rst.split('\n')]
		for line in rlines:
			line = ' '.join(re.split(r'line\+',line))
			print('------------***'+str(line))
			#if line[1]==vmname:
			#	return line[2]
		return "none"

class synbotenv(object):
    """docstring for env"""
    def __init__(self, arg):
        super(synbotenv, self).__init__()
        self.arg = arg

    DISK_SYMBOL = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q'\
                  'r','s','t','u','v','w','x','y','z']
     
    APP_DISK_INDEX = {"es":0,"dn":0,"log":0,"tmp":0,"nn":0,"zk":0,"jn":0} 