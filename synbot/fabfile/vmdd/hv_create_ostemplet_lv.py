#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,hide
from fabric.colors import *

#prepare lv for ostemplet on the HV
def initostempletlv(vgapp,ostemplet_lv_size,lv_name,hvtempleturl):
    '''propre ostemplet lv on the remote host'''
    #res = run('test -e /dev/%s/ostemplet' % vgapp).failed
    with settings(warn_only=True),hide("everything"):
        if run('test -e /dev/%s/%s' % (vgapp,lv_name)).succeeded:
            run("umount -f /dev/%s/%s" % (vgapp,lv_name))
            run("lvremove -f /dev/%s/%s" % (vgapp,lv_name))
        run("lvcreate -L %s -nostemplet %s" % (ostemplet_lv_size,vgapp))
        run("mkfs.ext4 /dev/%s/%s" % (vgapp,lv_name))
        if run("test -e %s" % hvtempleturl).failed:  
            run("mkdir -p %s" % hvtempleturl)
        run("umount %s" % hvtempleturl)    
        run("mount /dev/%s/%s %s" % (vgapp,lv_name,hvtempleturl))

        #/etc/fstab
        run("sed -i '/%s/'d /etc/fstab" % lv_name)
        run("echo /dev/%s/%s %s ext4 defaults 0 2 >> /etc/fstab" % (vgapp,lv_name,hvtempleturl))
        
if __name__ == '__main__' :
    initostempletlv("vgapp")
