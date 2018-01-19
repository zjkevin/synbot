#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# The fabfile to scan host mem
# This fabfile can only work on Linux host with a valid SSH Key

from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,parallel,hide
from fabric.colors import *
from utils import load_vars
from utils import load_hosts
from sbc_utils import synbot_tools

__MOTHER_LAND = "mother_land"

SCAN_MEM_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_mem.tmp"

#env.hosts=['192.168.63.238','192.168.63.237']
#env.passwords={'192.168.63.237':'synway','192.168.63.238':'synway'}
cfg_vars = load_vars()

#installvmlisttemp.append('root@192.168.63.237')
env.roledefs.setdefault('mother_land',["root@%s" % str(h[1]) for h in load_hosts(__MOTHER_LAND)])

env.user = cfg_vars['iuser']
env.password = cfg_vars['ipwd']

@task
@roles('mother_land')
@parallel
def hv_mem_scan():
    with settings(warn_only=True),hide("output"),hide("warnings"):    
        ret = run("cat /proc/meminfo |grep MemTotal")
        __lines = ret.strip().split(" ")
        __f_mem = open(SCAN_MEM_TMP_FILE,"a")
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        for __l in __lines:
            try:
                if __l.strip().lower() not in ("","kb","memtotal:"):
                    __mem_size = "%.2f" % (float(int(__l))/1024/1024)
                    __f_mem.write("%s: %s\n" % (host_name,__mem_size))
            except Exception, e:
                print e
        __f_mem.close()
        __f_mem.close()



