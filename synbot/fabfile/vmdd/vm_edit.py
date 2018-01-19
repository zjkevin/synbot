#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,hide
from fabric.colors import *

def edithost(hostname,nameserver,ip,network,gateway,netmask,vgos="poc5",vgapp="poc5",rootmounter="/root/imgtemp"):
    '''edit text'''
    with settings(warn_only=True),hide("output") :
        run("mkdir -p %s" % rootmounter)
        run("umount -f %s" % rootmounter)
        #find idle loopback device
        #if kpartx a img ,it will auto use a loop device if you use a lv ,because lv is a device already
        #so need not use loop divice, use kpartx is enough
        loopdev = str(run("losetup -f"))
        run("losetup %s /dev/%s/%sos" % (loopdev,vgos,hostname))
        run("kpartx -a %s" % loopdev)

        run("vgchange -ay vg_vmos")
        run("mount /dev/vg_vmos/lvroot %s" % rootmounter)
        cd("%s" % rootmounter)

        run("echo %s > %s/etc/hostname" % (hostname,rootmounter))
        run("echo nameserver %s > %s/etc/resolv.conf" % (nameserver,rootmounter))

        run("echo %s > %s/etc/network/interfaces" % ("auto lo",rootmounter))
        run("echo %s >> %s/etc/network/interfaces" % ("iface lo inet loopback",rootmounter))
        
        run("echo %s >> %s/etc/network/interfaces" % ("auto eth0",rootmounter))
        run("echo %s >> %s/etc/network/interfaces" % ("iface eth0 inet static",rootmounter))
        run("echo address %s >> %s/etc/network/interfaces" % (ip,rootmounter))
        run("echo netmask %s >> %s/etc/network/interfaces" % (netmask,rootmounter))
        run("echo network %s >> %s/etc/network/interfaces" % (network,rootmounter))
        run("echo gateway %s >> %s/etc/network/interfaces" % (gateway,rootmounter))
        cd("/root")

        # if run("test -f %s" % "/vm/ostemplet/hosts").succeeded:
        #    run("mv /vm/ostemplet/hosts %s/etc/hosts" % rootmounter)
        #     run("echo 127.0.1.1 %s >> %s/etc/hosts" % (hostname,rootmounter))

        run("echo /dev/vdb none swap sw 0 0 >> %s/etc/fstab" % rootmounter)
        
        run("umount -f /dev/vg_vmos/lvroot")
        run("lvchange -a n /dev/vg_vmos/lvroot")
        run("vgchange -a n vg_vmos")
        run("kpartx -d %s" % loopdev)
        run("losetup -d %s" % loopdev)

        #swap
        loopdev = str(run("losetup -f"))
        run("losetup %s /dev/%s/%sswap" % (loopdev,vgapp,hostname))
        run("mkswap -f %s" % loopdev)
        run("losetup -d %s" % loopdev)
        #fdisk vdd
        # loopdev = str(run("losetup -f"))
        # run("losetup %s /dev/%s/%sapp" % (loopdev,vgapp,hostname))
        # run("fdisk  %s<<EOF\nd\nn\np\n1\n \n \nw\nEOF" % loopdev)
        # run("losetup -d %s" % loopdev)   
        
        # run("mount /dev/%s/%sapp %s" % (vgapp,hostname,rootmounter)
        # cd("%s" % rootmounter)
        # run("mkdir -p log")
        # run("mkdir -p syntmp")
        # run("mkdir -p mail")
        # run("mkdir -p syn_init_once")
        # run("umount -f %s" % rootmounter)
        #add to vg_vmapp
        run("virsh define /vm/ostemplet/%s.xml" % hostname)
        print(green("init %s on %s is done!!!!" % (hostname,env.host_string)))
  

if __name__ == '__main__':
    edithost("p2n10","192.168.60.171","192.168.63.30","198.168.63.0","192.168.63.254")