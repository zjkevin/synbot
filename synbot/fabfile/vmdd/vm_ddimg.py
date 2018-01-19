#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,get,hide
from fabric.colors import *

import utils

def ddimg(vmname,vgos,vgapp):
    '''dd img on the remote host'''
    print(green("start dd process for vm:%s" % vmname))
    with settings(warn_only=True),hide("output"):
        if utils.lvexist("%sos" % vmname, "%s" % vgos):
            run("dd if=/vm/ostemplet/debian71.img of=/dev/%s/%sos bs=4M" % (vgos,vmname))
        else :
            print(red("dd /dev/%s/%sos not exist!" % (vgos,vmname)))
           
if __name__ == '__main__' :
    ddimg("p2n1")
