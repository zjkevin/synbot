#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, settings,local,hide
from fabric.colors import *

import re
import utils
import copy

_DISK_SYMBOL = utils.synbotenv.DISK_SYMBOL

def createvmlv(hostname,vgos,vgapp,os_size,swap_size,disk_exts):
    '''prepare lv for vm on the remote host'''
    with settings(warn_only=True),hide("output"):
        if not utils.lvexist("%sos" % hostname,"%s" % vgos):
            run("lvcreate -L %s -n%sos %s" % (os_size,hostname,vgos))
        if not utils.lvexist("%sswap" % hostname,"%s" % vgapp):
            run("lvcreate -L %s -n%sswap %s" % (swap_size,hostname,vgapp))
        
        app_disk_index =copy.deepcopy(utils.synbotenv.APP_DISK_INDEX)
        print green(disk_exts)
        for d in disk_exts:
            if not utils.lvexist("%s_%s%s" % (hostname,d["name"],app_disk_index[d["name"]] + 1) ,d["info"]["vg"]):
                if d["info"]["pvs"].strip() == "":
                    run("lvcreate -L %s -n%s_%s%s %s" % (d["info"]["size"],hostname,d["name"],app_disk_index[d["name"]] + 1,d["info"]["vg"]))
                else:
                    run("lvcreate -L %s -n%s_%s%s %s %s" % (d["info"]["size"],hostname,d["name"],app_disk_index[d["name"]] + 1,d["info"]["vg"],d["info"]["pvs"]))
            app_disk_index[d["name"]] = app_disk_index[d["name"]] + 1

def create_fdiskvdd(disk_exts,cn_templet_url,hostname):
    app_disk_index= copy.deepcopy(utils.synbotenv.APP_DISK_INDEX)
    f = open("%s/%s_lvextend.py" % (cn_templet_url,hostname),"w")
    f.write("import os\n")
    f.write("def lvextend():\n")
    disk_index = 0
    
    vgcreate_flag = False
    for d in disk_exts:
        f.write("    os.system(\"pvcreate /dev/vd%s\")\n" % _DISK_SYMBOL[disk_index])
        if not vgcreate_flag:
            f.write("    os.system(\"vgcreate vg_vmapp /dev/vd%s\")\n" % _DISK_SYMBOL[disk_index])
            vgcreate_flag = True
        else:
            f.write("    os.system(\"vgextend vg_vmapp /dev/vd%s\")\n" % _DISK_SYMBOL[disk_index])
        f.write("    os.system(\"lvcreate -l %s -nlv%s%s vg_vmapp /dev/vd%s\")\n" % (_get_blocks(d["info"]["size"]),d["name"],app_disk_index[d["name"]] + 1,_DISK_SYMBOL[disk_index]))
        f.write("    os.system(\"mkfs.ext4 /dev/vg_vmapp/lv%s%s\")\n" % (d["name"],app_disk_index[d["name"]] + 1))
        if d["name"] == "log":
            f.write("    os.system(\"mount /dev/vg_vmapp/lv%s%s /var/%s\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"]))
        elif d["name"] == "tmp":
            f.write("    os.system(\"mount /dev/vg_vmapp/lv%s%s /%s\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"]))
        elif d["name"] == "dn":
            disk_index = app_disk_index[d["name"]] + 1 
            f.write("    os.system(\"mkdir -p /var/syndata/%s/d%s\")\n" %(d["name"],disk_index))
            f.write("    os.system(\"mkdir -p /var/syndata/%s/d%s/dn\")\n" %(d["name"],disk_index))
            f.write("    os.system(\"mkdir -p /var/syndata/%s/d%s/tmp\")\n" %(d["name"],disk_index))
            f.write("    os.system(\"chown -R hadoop:hadoop /var/syndata/%s/d%s\")\n" %(d["name"],disk_index))
        else:
            f.write("    os.system(\"mkdir -p /var/syndata/%s/d%s\")\n" %(d["name"],app_disk_index[d["name"]] + 1))
            f.write("    os.system(\"chown -R hadoop:hadoop /var/syndata/%s/d%s\")\n" %(d["name"],app_disk_index[d["name"]] + 1))
            f.write("    os.system(\"mount /dev/vg_vmapp/lv%s%s /var/syndata/%s/d%s\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"],app_disk_index[d["name"]] + 1))
        f.write("    os.system(\"sed -i '/lv%s%s/'d /etc/fstab\")\n" % (d["name"],app_disk_index[d["name"]] + 1))
        if d["name"] == "log":
            f.write("    os.system(\"sed -i '$a /dev/vg_vmapp/lv%s%s /var/%s ext4 defaults 0 2' /etc/fstab\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"]))
        elif d["name"] == "tmp":
            f.write("    os.system(\"sed -i '$a /dev/vg_vmapp/lv%s%s /%s ext4 defaults 0 2' /etc/fstab\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"]))
        else:
            f.write("    os.system(\"sed -i '$a /dev/vg_vmapp/lv%s%s /var/syndata/%s/d%s ext4 defaults 0 2' /etc/fstab\")\n" % (d["name"],app_disk_index[d["name"]] + 1,d["name"],app_disk_index[d["name"]] + 1))
        disk_index = disk_index + 1
        app_disk_index[d["name"]] = app_disk_index[d["name"]] + 1
    f.write("    os.system(\"mount -a\")\n")
    f.write("if __name__ == '__main__':\n")
    f.write("    lvextend()")
    f.close()
    #create es and hdfs data config yaml and ansible
    local("mkdir -p %s/%s" % (cn_templet_url,hostname))
    f_es = open("%s/%s/es_data_mount.yml" % (cn_templet_url,hostname),"w")
    f_es.write("---\n")
    f_es.write("es_data_mount: \n")
    if app_disk_index["es"] > 0:
        for i in range(app_disk_index["es"]):
            f_es.write(" - %s/d%s\n" % ("/var/syndata/es",i+1))
    f_es.close()

    f_hdfs = open("%s/%s/hdfs_data_mount.yml" % (cn_templet_url,hostname),"w")
    f_hdfs.write("---\n")
    f_hdfs.write("hdfs_data_mount: \n")
    if app_disk_index["dn"] > 0:
        for i in range(app_disk_index["dn"]):
            f_hdfs.write(" - %s/d%s\n" % ("/var/syndata/dn",i+1))
    f_hdfs.write("hdfs_data_mount_dn: \n")
    if app_disk_index["dn"] > 0:
        for i in range(app_disk_index["dn"]):
            f_hdfs.write(" - %s/d%s/dn\n" % ("/var/syndata/dn",i+1))
    f_hdfs.write("hdfs_data_mount_tmp: \n")
    if app_disk_index["dn"] > 0:
        for i in range(app_disk_index["dn"]):
            f_hdfs.write(" - %s/d%s/tmp\n" % ("/var/syndata/dn",i+1))
    f_hdfs.close()        


def _get_blocks(lv_size):  
    re_str = "(\d+.*\d*)G"
    re_pat = re.compile(re_str)
    search_ret = re_pat.search(lv_size)
    blocks = 0
    if search_ret:
        blocks = int(float(search_ret.groups()[0]))
    return blocks*1024/4-1
