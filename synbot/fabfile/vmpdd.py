#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# The fabfile to start a cluster composed of virtual machines(vm).
# This fabfile can only work on Linux host with a valid SSH Key

from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,parallel,hide
import os, sys, uuid, random
from xml.etree import ElementTree as XmlTree
from utils import *
from fabric.colors import *
from vmdd.utils import vminfo
import yaml
import logging
import logging.config
import codecs

from vmdd import vm_remove_lv
from vmdd import vm_create_lv
from vmdd import vm_create_xml
from vmdd import vm_ddimg
from vmdd import vm_edit

from vmdd import hv_create_ostemplet_lv
from vmdd import hv_img_prepare

from sbc_utils import synbot_tools
from sbc_utils import synbot_fabric
import copy

with codecs.open('./conf/logging.yaml', 'r', 'utf-8') as logging_file:
  logging.config.dictConfig(yaml.load(logging_file))

_logger = logging.getLogger(__name__)


_INSTALLVM_FLAG = "installvm"
_REMOVEVM_FLAG = "removevm"
_UPDATEIMG_FLAG = "updateimg"
_STARTVM_FLAG = "startvm"
_HALTVM_FLAG = "haltvm"
_HALTHV_FLAG = "halthv"


SCAN_PARTITION_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_partition.tmp"
SCAN_DISK_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_dick.tmp"
SCAN_PV_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_pv.tmp"
SCAN_VM_TMP_FILE = synbot_tools.current_file_directory() + "/../tmp/scan_vm.tmp"
VM_RESOURCE_FILE = "./cluster_config/vm_resource.yml"
CLUSTER_IP_FILE = synbot_tools.current_file_directory() + "/../cluster_config/cluster_ip.yml"
CLUSTER_DISK_CONFIG = synbot_tools.current_file_directory() + "/../cluster_config/cluster_disk_config.yml"
IP_TEMPLATES_FILE = "./templates/hv_interfaces.temp"

cluster_ip_dict = {}
if os.path.exists(CLUSTER_IP_FILE):
    cluster_ip_f = open(CLUSTER_IP_FILE,"r")
    cluster_ip_dict = yaml.load(cluster_ip_f)
else:
    print red("cluster_config/cluster_ip.yml is missing please execute 'sbc -en' to edit network config then execute 'sbc -hosts' to create")
    sys.exit(1)

#env.hosts=['192.168.63.238','192.168.63.237']
#env.passwords={'192.168.63.237':'synway','192.168.63.238':'synway'}
cfg_vars = load_vars()
installvmlist = load_hosts(_INSTALLVM_FLAG)
removevmlist = load_hosts(_REMOVEVM_FLAG)
updateimghvlist = load_hosts(_UPDATEIMG_FLAG)
startvmlist = load_hosts(_STARTVM_FLAG)
haltvmlist = load_hosts(_HALTVM_FLAG)
halthvlist = load_hosts(_HALTHV_FLAG)
mother_land_list = load_hosts("mother_land")

#vmconfig={}
vmconfig = load_hostsip_config()
hostsiplist=vmconfig['hostsiplist']
vg_conf = vmconfig["vg_conf"]
hostsnetworklist=vmconfig['hostsnetworklist']
diskextslist=vmconfig['diskextslist']
#print cyan(diskextslist)

#installvmlisttemp.append('root@192.168.63.237')
env.roledefs.setdefault('updateimg',["root@%s" % str(h[1]) for h in updateimghvlist])
env.roledefs.setdefault('installvm',["root@%s" % str(h[0]) for h in installvmlist])
env.roledefs.setdefault('removevm',["root@%s" % str(h[0]) for h in removevmlist])
env.roledefs.setdefault('startvm',["root@%s" % str(h[0]) for h in startvmlist])
env.roledefs.setdefault('haltvm',["root@%s" % str(h[0]) for h in haltvmlist])
env.roledefs.setdefault('halthv',["root@%s" % str(h[1]) for h in halthvlist])
env.roledefs.setdefault('mother_land',["root@%s" % str(h[1]) for h in mother_land_list])

env.user = cfg_vars['iuser']
env.password = cfg_vars['ipwd']

#[['poc2.dev.s', 'p2n7.dev.s'], ['poc3.dev.s', 'p3n8.dev.s'], ['poc4.dev.s', 'p4n7.dev.s'], ['poc6.dev.s', 'p6n8.dev.s']]
#env.roledefs={'getimg':['root@192.168.63.231','root@192.168.63.232'
#,'root@192.168.63.233','root@192.168.63.234','root@192.168.63.235'
#,'root@192.168.63.236','root@192.168.63.237','root@192.168.63.238'],'installvm':['root@192.168.63.237']}

def _get_img_to_hv_(cntempleturl,hvtempleturl,vgapp,file_items,unzip_imgs,ostemplet_lv_size,lv_name):
    #init lv on the HV for store img
    hv_create_ostemplet_lv.initostempletlv(vgapp,ostemplet_lv_size,lv_name,hvtempleturl)
    #copy img from CN to the HV
    hv_img_prepare.prepareimg(True,cntempleturl,hvtempleturl,file_items,unzip_imgs)

def _create_lv_for_vm_(vmname,nameserver,ip,network,gateway,netmask,vgos,vgapp,os_size,swap_size,disk_exts,mem,current_mem,vcpu,hv_ostemplet_url,cn_templet_url):
    #remove lv
    vm_remove_lv.removevmlv(vmname)
    #create lv
    vm_create_lv.createvmlv(vmname,vgos,vgapp,os_size,swap_size,disk_exts)
    #create fdiskvdd.py
    vm_create_lv.create_fdiskvdd(disk_exts,cn_templet_url,vmname)    
    #create xml
    vm_create_xml.createxml(vmname,mem,current_mem,vcpu,vgos,vgapp,hv_ostemplet_url,cn_templet_url,disk_exts)
    #dd
    vm_ddimg.ddimg(vmname,vgos,vgapp)
    #edit host
    vm_edit.edithost(vmname,nameserver,ip,network,gateway,netmask,vgos=vgos,vgapp=vgapp)

def start_vm(vmname):
    if not vminfo(vmname)=='running':
        run("virsh start %s" % vmname)

def shutdown_vm(vmname):
    if not vminfo(vmname)=='shut off':
        run("virsh shutdown %s" % vmname)
    
@task
@roles('updateimg')
@parallel
def hv_prepareimg():
    '''prepare img on the HV where set in file host node [updateimg]
        it will prepare a LV in 5G for the vm img to store
        if there is already have a lv called /dev/vg/ostemplet
        it will be rebuild 
        Arguments:
        cntempleturl:    the folder where store templet img on the CN 
        hvtempleturl:    the folder where store templet img on the HV
        vgapp:           the vg on the HV which you want to create lv for img on
    '''
    cntempleturl = cfg_vars["cntemplet_url"]
    hvtempleturl = cfg_vars["mount_ostemplet"]
    vgapp = cfg_vars["vg_name"]
    file_items = cfg_vars["file_items"]
    unzip_imgs = cfg_vars["unzip_imgs"]
    ostemplet_lv_size = cfg_vars["ostemplet_lv_size"]
    lv_name = cfg_vars["lv_name"]

    execute(_get_img_to_hv_,cntempleturl,hvtempleturl,vgapp,file_items.split(","),unzip_imgs.split(","),ostemplet_lv_size,lv_name)

@task
@roles('halthv')
@parallel
def hv_shutdown():
    '''shutdown HV where set in file host node [halthv]'''
    if(env.host_string==None):
        return
    if(env.host_string.find("@")):
        if(env.host_string.find(".")):
            hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
        else:
            hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
    else:
        hvname=env.host_string
    run("halt")

@task
@roles('startvm')
@parallel
def vm_start():
    '''start vm  on the HV where set in file host node [startvm]'''
    if(env.host_string==None):
        return
    if(env.host_string.find("@")):
        if(env.host_string.find(".")):
            hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
        else:
            hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
    else:
        hvname=env.host_string
    vms=[]
    global startvmlist
    global hostsnetworklist
    for v in startvmlist:
        if 'root@'+str(v[0])==env.host_string:
            vms.append(v[1])

    for v in vms:
        vmname=v.split('.')[0]
        start_vm(vmname)

@task
@roles('haltvm')
@parallel
def vm_halt():
    '''shutdown vm on the HV where set in file host node [haltvm]'''
    if(env.host_string==None):
        return
    if(env.host_string.find("@")):
        if(env.host_string.find(".")):
            hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
        else:
            hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
    else:
        hvname=env.host_string
    vms=[]
    global haltvmlist
    global hostsnetworklist
    for v in haltvmlist:
        if 'root@'+str(v[0])==env.host_string:
            vms.append(v[1])

    for v in vms:
        vmname=v.split('.')[0]
        shutdown_vm(vmname)        

@task
@roles('installvm')
@parallel
def vm_init():
    '''init vm on the HV where set in file host node [installvm]'''
    if(env.host_string==None):
        return
    if(env.host_string.find("@")):
        if(env.host_string.find(".")):
            hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
        else:
            hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
    else:
        hvname=env.host_string
    vms=[]
    global installvmlist
    global hostsiplist
    global hostsnetworklist
    global diskextslist
    for v in installvmlist:
        if 'root@'+str(v[0])==env.host_string:
            vms.append(v[1])
    #load vm parameter
    os_size = cfg_vars["os_size"]
    swap_size = cfg_vars["swap_size"]

    mem = cfg_vars["mem"]
    current_mem =cfg_vars["current_mem"] 
    vcpu = cfg_vars["vcpu"]

    hvtempleturl = cfg_vars["mount_ostemplet"]
    cn_templet_url = cfg_vars["cntemplet_url"]
    for v in vms:
        vmname=v.split('.')[0]
        #load vm resource
        f = open(VM_RESOURCE_FILE,"r")
        vm_resource_dict = yaml.load(f)
        if isinstance(vm_resource_dict,dict) and vm_resource_dict.has_key(vmname):
            mem = vm_resource_dict[vmname]["mem"]
            current_mem = vm_resource_dict[vmname]["current_mem"] 
            vcpu = vm_resource_dict[vmname]["cpu"]
        ip=hostsiplist[v.split('.')[0]]
        ipsect=ip[0:ip.rfind('.')]
        netmask=hostsnetworklist[ipsect].split(' ')[1]
        network=hostsnetworklist[ipsect].split(' ')[2]
        gateway=hostsnetworklist[ipsect].split(' ')[3]
        nameserver=hostsnetworklist[ipsect].split(' ')[4]
        vgos = vg_conf[hvname]["os"] if vg_conf.has_key(hvname) else "vgos"
        vgapp = vg_conf[hvname]["app"] if vg_conf.has_key(hvname) else "vgapp"
        disk_exts = []
        if diskextslist.has_key(vmname):
            disk_exts = diskextslist[vmname]
        else:
            print(red("vm:%s miss disk config in cluster_config/cluster_disk_config.yml" % vmname))
        print(green("vminfo: name-%s ip-%s netmask-%s network-%s gateway-%s nameserver-%s hvname-%s vgos-%s vgapp-%s" % 
            (vmname,ip,netmask,network,gateway,nameserver,hvname,vgos,vgapp)))
        print yellow(disk_exts)
        _create_lv_for_vm_(vmname,nameserver,ip,network,gateway,netmask,vgos,vgapp,os_size,swap_size,disk_exts,mem,current_mem,vcpu,hvtempleturl,cn_templet_url)

@task
@roles('removevm')
@parallel
def vm_remove():
    '''remove vms on HV where set in file hostcfg node [removevm] '''
    global removevmlist
    if(env.host_string==None):
        return
    if(env.host_string.find("@")):
        if(env.host_string.find(".")):
            hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
        else:
            hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
    else:
        hvname=env.host_string
    vms=[]
    for v in removevmlist:
        if 'root@'+v[0]==env.host_string:
            vms.append(v[1])
    for v in vms:
        vmname=v.split('.')[0]   
        vm_remove_lv.removevmlv(vmname)

@task
@roles('pipinit')
@parallel
def vm_pipinit():
    '''init pip packages '''
    __pip_server = "http://192.168.50.31:8080"
    run("apt-get install build-essential")
    run("apt-get install python2.7-dev")
    run("apt-get install python-setuptools")
    run("apt-get install MySQL-python")
    run("export PIP_INDEX_URL=http://www.repo.s/pypi/simple")
    run("pip install fabric --no-index --find-links %s" % __pip_server)
    run("pip install ansible --no-index --find-links %s" % __pip_server)
    run("pip install kazoo --no-index --find-links %s" % __pip_server)
    run("pip install jinja2 --no-index --find-links %s" % __pip_server)
    run("pip install requests --no-index --find-links %s" % __pip_server)
    run("pip install paste --no-index --find-links %s" % __pip_server)
    run("pip install bottle --no-index --find-links %s" % __pip_server)
    run("pip install thrift --no-index --find-links %s" % __pip_server)
    run("pip install pyes --no-index --find-links %s" % __pip_server)
    run("pip install nose --no-index --find-links %s" % __pip_server)
    run("pip install happybase --no-index --find-links %s" % __pip_server)
    run("pip install behave --no-index --find-links %s" % __pip_server)
    run("pip install thrift --no-index --find-links %s" % __pip_server)
    run("pip install pyes --no-index --find-links %s" % __pip_server)
    run("pip install nose --no-index --find-links %s" % __pip_server)
    run("pip install happybase --no-index --find-links %s" % __pip_server)
    run("pip install behave --no-index --find-links %s" % __pip_server)   

@task
@roles('mother_land')
@parallel
def hv_pv_scan():
    '''scan hv pv which set in [mother_land] and will create a yml file in synbot root
    '''
    #hide("output")
    with settings(warn_only=True),hide("warnings"):    
        ret = run("pvs")
        lines = ret.split("\n")
        f = open(SCAN_PV_TMP_FILE,"a")
        disk_index = 1
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        f.write("[%s]\n" % host_name)
        for l in lines:
            temp = ",".join(l.strip().split())
            temp_l = temp.split(",")
            if temp_l[1] == "vgos":
                f.write("disk_os:"+",".join(l.strip().split())+"\n")
            elif temp_l[1] == "vgapp":
                f.write("disk%s:" % disk_index+",".join(l.strip().split())+"\n")
                disk_index = disk_index + 1
        f.close()

@task
@roles('mother_land')
@parallel
def format_disk_on_hv():
    '''
    format disk on hv depend on file:cluster_config/cluster_disk_config.yml
    '''
    with settings(warn_only=True),hide("output"),hide("warnings"):
        f = open(CLUSTER_DISK_CONFIG,'r')
        cluster_disk_config_dict = yaml.load(f)
        f.close()
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        disk_config_list = cluster_disk_config_dict[host_name]
        app_disk_index = copy.deepcopy(synbot_fabric.synbotenv.APP_DISK_INDEX)
        for d_c in disk_config_list:
            #- {disk: /dev/sda5, mount: null, name: nn, size: 10G}
            app_disk_index[d_c["name"]] = app_disk_index[d_c["name"]] + 1
            run("sed -i '/%s/'d /etc/fstab" % d_c["disk"])
            run("mount -a")
            run("mkfs.ext4 %s" % d_c["disk"])
            if d_c["name"] == "log":
                run("sed -i '$a %s /var/%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"]))
            elif d_c["name"] == "tmp":
                run("sed -i '$a %s /%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"]))
            elif d_c["name"] == "dn":
                run("sed -i '$a %s /var/syndata/%s/d%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"],app_disk_index[d_c["name"]]))
                run("mkdir -p /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
                run("mkdir -p /var/syndata/%s/d%s/dn" % (d_c["name"],app_disk_index[d_c["name"]]))
                run("mkdir -p /var/syndata/%s/d%s/tmp" % (d_c["name"],app_disk_index[d_c["name"]]))
                run("chown -R hadoop:hadoop /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
            else:
                run("sed -i '$a %s /var/syndata/%s/d%s ext4 defaults 0 2' /etc/fstab" % (d_c["disk"],d_c["name"],app_disk_index[d_c["name"]]))
                run("mkdir -p /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
                run("chown -R hadoop:hadoop /var/syndata/%s/d%s" % (d_c["name"],app_disk_index[d_c["name"]]))
            run("mount -a")

@task
@roles('mother_land')
@parallel
def hv_disk_scan():
    with settings(warn_only=True),hide("output"),hide("warnings"):
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        if host_name in ('poc1','poc2'):                   
            ret = run("parted -l|grep Disk|grep dev|grep sd[d-z]")
        else:
            ret = run("parted -l|grep Disk|grep dev|grep sd[b-z]")
        lines = ret.split("\n")
        f = open(SCAN_PARTITION_TMP_FILE,"a")
        f_disk = open(SCAN_DISK_TMP_FILE,"a")
        disk_index = 1
        _logger.info("dealing with disk on hosts:%s" % host_name)
        f.write("[%s]\n" % host_name)
        f_disk.write("[%s]\n" % host_name)
        _logger.info("disk info lines:\n%s" % "\n".join(lines))
        __disk_dict = []
        __partition_dict = []
        for l in lines:
            _logger.info("dealing with:%s" % l)
            if "WARNING:" in l or l.strip()=="" or "mapper" in l or "partition" in l:
                _logger.info("inefficacy")
            else:
                __disk = "".join(l).strip().split()[1:][0].replace(":","")
                __disk_space = "".join(l).strip().split()[1:][1].replace(":","")
                _logger.info("get disk name:%s" % __disk)
                __disk_dict.append(__disk)
                run("parted %s mklabel gpt -s" % __disk)
                run("parted %s rm 1" % __disk)
                run("parted %s mkpart primary 2048s %s" % (__disk,__disk_space))                
                ret_p = run("fdisk -l |grep %s | grep /dev" % __disk)
                _logger.info("info for disk:%s \n%s" %(__disk,ret_p))
                lines_p = ret_p.split("\n")
                for l_p in lines_p:
                    if "WARNING:" in l_p or l_p.strip()=="" or "mapper" in l_p or "partition" in l_p:
                       _logger.info("inefficacy")
                    else:
                        _logger.info("disk string:%s" % l_p)
                        l_p_s = l_p.strip().split()
                        if not l_p_s[0] == "Disk" and l_p_s[4] not in ('5','82') and l_p_s[1] not in ("*"):
                            _logger.info("hit the target")
                            __partition_dict.append(l_p_s[0])
                        else:
                            _logger.info("missing")
        __disk_dict.sort()
        __partition_dict.sort()
        for i in __disk_dict:
            f_disk.write("%s\n" % i)
        f_disk.close()
        for i in __partition_dict:
            f.write("%s\n" % i)
        f.close()
        print(__disk_dict)
        print(__partition_dict)

@task
@roles('mother_land')
@parallel
def network_interfaces_edit():
    with settings(warn_only=True),hide("output"),hide("warnings"):
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        _ip = ""
        _domain = "dev.s"
        _netmask = "255.255.255.0"
        _gateway = ""
        _nameserver = ""
        if cluster_ip_dict.has_key("ipaddress"):
            if cluster_ip_dict["ipaddress"][host_name]:
                _ip = cluster_ip_dict["ipaddress"][host_name]
        _ip_segment = ".".join(_ip.split(".")[:-1])
        if cluster_ip_dict.has_key("domain"):
            _domain = cluster_ip_dict["domain"]
        if cluster_ip_dict.has_key(_ip_segment):
            _domain = cluster_ip_dict[_ip_segment]["domain"]
            _netmask = cluster_ip_dict[_ip_segment]["netmask"]
            _gateway = cluster_ip_dict[_ip_segment]["gateway"]
            _nameserver = cluster_ip_dict[_ip_segment]["nameserver"]

        run("echo nameserver %s > /etc/resolv.conf" % (_nameserver))
        network_interfaces_file = open(IP_TEMPLATES_FILE,"r")
        run("echo '# This file describes the network interfaces available on your system' > /etc/network/interfaces")
        for l in network_interfaces_file.readlines():
            print red(l)
            if "{{" in l:
                l = l.replace("{{ip}}",_ip).replace("{{domain}}",_domain).replace("{{gateway}}",_gateway).replace("{{netmask}}",_netmask)
                print yellow(l)
            print cyan("echo %s >> /etc/network/interfaces" % l)
            run("echo %s >> /etc/network/interfaces" % l.replace("\n","").replace("\r",""))
        network_interfaces_file.close()
        run("service networking restart")

@task
@roles('mother_land')
@parallel
def hv_vm_scan():
    with settings(warn_only=True),hide("output"),hide("warnings"):    
        ret = run("virsh list --all|grep p")
        lines = ret.split("\n")
        f = open(SCAN_VM_TMP_FILE,"a")
        host_name = env.host_string
        host_name = env.host_string.split("@")[1] if "@" in env.host_string else env.host_string
        host_name = host_name.split(".")[0] if "." in host_name else host_name
        f.write("[%s]\n" % host_name)
        for l in lines:
            temp = ",".join(l.strip().split())
            temp_l = temp.split(",")
            if len(l.strip().split()) > 1:
                f.write(l.strip().split()[1]+"\n")
        f.close()