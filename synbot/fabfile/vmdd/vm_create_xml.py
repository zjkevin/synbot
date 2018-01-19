#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os,uuid,random
from xml.etree import ElementTree as XmlTree
from fabric.api import run, execute, put, settings, cd ,local ,task
from utils import *
import copy

_DISK_SYMBOL = synbotenv.DISK_SYMBOL

def _mac_gen_():
    mac = [0x00,0x16,0x3e,
            random.randint(0x00,0x7f),
            random.randint(0x00,0xff),
            random.randint(0x00,0xff),
               ]
    return ":".join(map(lambda x: "%02x" % x, mac)) 

def createxml(hostname,mem,current_mem,vcpu,vgos,vgapp,hv_ostemplet_url,cn_templet_url,disk_exts):
    '''edit vmxml'''
    if not os.path.exists("%s/vmtemplet.xml" % cn_templet_url) :
        print "vm templet xml not find in /vm/ostemplet"
    else:
        xml = XmlTree.parse("%s/vmtemplet.xml" % cn_templet_url)

        vm_items = (("./name", hostname ),
            ("./uuid", uuid.uuid1()),
            ("./memory", mem),
            ("./currentMemory", current_mem),
            ("./vcpu", vcpu))

        # disk_items=(("vda","/dev/%s/%sos" % (vgos,hostname)),
        #     ("vdb","/dev/%s/%svar" % (vgos,hostname)),
        #     ("vdc","/dev/%s/%sswap" % (vgapp,hostname)),
        #     ("vdd","/dev/%s/%sapp" % (vgapp,hostname)))

        disk_items=(("vda","/dev/%s/%sos" % (vgos,hostname)),
            ("vdb","/dev/%s/%sswap" % (vgapp,hostname)))

        for t, v in vm_items :
            xml.find(t).text = str(v)

        for ele in xml.findall("./devices/disk[@device='disk']") :
            if ele.attrib["type"] == "block" : 
                eleDisk = ele
                eleDisk.find("driver").set("type","raw")
                for t,v in disk_items:
                    if(eleDisk.find("target").get("dev")==t):
                        eleDisk.find("source").set("dev",v); 
        
        eleIF = xml.find("./devices/interface[@type='bridge']")
        eleIF.find("mac").set("address", _mac_gen_())

        #-configinfo:p7n1 hdfs|/dev/sdc|100G,es|/dev/sdd|100G,log|/dev/sdc|100G
        #disk xml define
        app_disk_index= copy.deepcopy(synbotenv.APP_DISK_INDEX)
        disk_index = 0            
        eleDevice = xml.find("./devices")
        for d in disk_exts:
            item_device = XmlTree.Element("disk",{"type":"block","device":"disk"})
            item_device.append(XmlTree.Element("driver",{"name":"qemu","type":"raw"}))
            item_device.append(XmlTree.Element("source",{"dev":"/dev/%s/%s_%s%s" % (d["info"]["vg"],hostname,d["name"],app_disk_index[d["name"]] + 1)}))
            item_device.append(XmlTree.Element("target",{"dev":"vd%s" % _DISK_SYMBOL[disk_index],"bus":"virtio"}))
            eleDevice.append(item_device)
            disk_index = disk_index + 1
            app_disk_index[d["name"]] = app_disk_index[d["name"]] + 1 

        xml.write("%s/%s.xml" % (cn_templet_url,hostname),"UTF-8")
        put("%s/%s.xml" % (cn_templet_url,hostname),"%s/%s.xml" % (hv_ostemplet_url,hostname))

if __name__ == '__main__':
    createxml("p3n1_test",2,2,2,"vgos","vgapp","/vm/ostemplet","/vm/ostemplet")