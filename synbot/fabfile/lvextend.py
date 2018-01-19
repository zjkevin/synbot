# #!/usr/bin/env python
# # -*- coding: UTF-8 -*-
# #
# # The fabfile to start a cluster composed of virtual machines(vm).
# # This fabfile can only work on Linux host with a valid SSH Key

# from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,parallel
# import os, sys, uuid, random
# from xml.etree import ElementTree as XmlTree
# from utils import *
# from fabric.colors import *
# from vmdd.utils import vminfo

# from vmdd import vm_remove_lv
# from vmdd import vm_create_lv
# from vmdd import vm_create_xml
# from vmdd import vm_ddimg
# from vmdd import vm_edit

# from vmdd import hv_create_ostemplet_lv
# from vmdd import hv_img_prepare

# _INSTALLVM_FLAG = "installvm"
# _REMOVEVM_FLAG = "removevm"
# _UPDATEIMG_FLAG = "updateimg"
# _STARTVM_FLAG = "startvm"
# _HALTVM_FLAG = "haltvm"
# _HALTHV_FLAG = "halthv"
# _PIP_INIT_FLAG = "pipinit"

# #env.hosts=['192.168.63.238','192.168.63.237']
# #env.passwords={'192.168.63.237':'synway','192.168.63.238':'synway'}
# cfg_vars = load_vars()
# installvmlist = load_hosts(_INSTALLVM_FLAG)
# removevmlist = load_hosts(_REMOVEVM_FLAG)
# updateimghvlist = load_hosts(_UPDATEIMG_FLAG)
# startvmlist = load_hosts(_STARTVM_FLAG)
# haltvmlist = load_hosts(_HALTVM_FLAG)
# halthvlist = load_hosts(_HALTHV_FLAG)
# pipinitlist = load_hosts(_PIP_INIT_FLAG)

# installvmlisttemp=[]
# removevmlisttemp=[]
# updateimghvlisttemp=[]
# starthvlisttemp=[]
# halthvlisttemp=[]
# halthvownelisttemp=[]
# pipinitlisttemp=[]

# #vmconfig={}
# vmconfig=load_hostsip_config()

# hostsiplist=vmconfig['hostsiplist']
# hostsnetworklist=vmconfig['hostsnetworklist']

# for v in installvmlist:
#     installvmlisttemp.append('root@'+str(v[0]))

# for v in removevmlist:
#     removevmlisttemp.append('root@'+str(v[0]))

# for v in startvmlist:
#     starthvlisttemp.append('root@'+str(v[0]))

# for v in pipinitlist:
#     pipinitlisttemp.append('root@'+str(v[0]))   

# for v in haltvmlist:
#     halthvlisttemp.append('root@'+str(v[0]))       

# for v in updateimghvlist:
#     updateimghvlisttemp.append('root@'+str(v[1]))

# for v in halthvlist:
#     halthvownelisttemp.append('root@'+str(v[1]))      

# #installvmlisttemp.append('root@192.168.63.237')
# env.roledefs.setdefault('updateimg',updateimghvlisttemp)
# env.roledefs.setdefault('installvm',installvmlisttemp)
# env.roledefs.setdefault('removevm',removevmlisttemp)
# env.roledefs.setdefault('startvm',starthvlisttemp)
# env.roledefs.setdefault('haltvm',halthvlisttemp)
# env.roledefs.setdefault('halthv',halthvownelisttemp)
# env.roledefs.setdefault('pipinit',pipinitlisttemp)

# #print(red(env.roledefs))
# env.user = cfg_vars['iuser']
# env.password = cfg_vars['ipwd']

# #[['poc2.dev.s', 'p2n7.dev.s'], ['poc3.dev.s', 'p3n8.dev.s'], ['poc4.dev.s', 'p4n7.dev.s'], ['poc6.dev.s', 'p6n8.dev.s']]
# #env.roledefs={'getimg':['root@192.168.63.231','root@192.168.63.232'
# #,'root@192.168.63.233','root@192.168.63.234','root@192.168.63.235'
# #,'root@192.168.63.236','root@192.168.63.237','root@192.168.63.238'],'installvm':['root@192.168.63.237']}

# def _get_img_to_hv_(cntempleturl,hvtempleturl,vgapp,file_items,unzip_imgs,ostemplet_lv_size,lv_name):
#     #init lv on the HV for store img
#     hv_create_ostemplet_lv.initostempletlv(vgapp,ostemplet_lv_size,lv_name,hvtempleturl)
#     #copy img from CN to the HV
#     hv_img_prepare.prepareimg(True,cntempleturl,hvtempleturl,file_items,unzip_imgs)

# def _create_lv_for_vm_(vmname,nameserver,ip,network,gateway,netmask,vgos,vgapp,os_size,app_size,swap_size,app_ext1_size,mem,current_mem,vcpu,hv_ostemplet_url,cn_templet_url):
#     #remove lv
#     vm_remove_lv.removevmlv(vmname,vgos,vgapp)
#     #create lv
#     vm_create_lv.createvmlv(vmname,vgos,vgapp,os_size,app_size,swap_size,app_ext1_size)
#     #create fdiskvdd.py
#     print red("app app app size size size size size size")
#     print cyan(app_ext1_size)
#     vm_create_lv.create_fdiskvdd(app_ext1_size,cn_templet_url)    
#     #create xml
#     vm_create_xml.createxml(vmname,mem,current_mem,vcpu,vgos,vgapp,hv_ostemplet_url,cn_templet_url)
#     #dd
#     vm_ddimg.ddimg(vmname,vgos,vgapp)
#     #edit host
#     vm_edit.edithost(vmname,nameserver,ip,network,gateway,netmask,vgos=vgos,vgapp=vgapp)

# def start_vm(vmname):
#     print(yellow(vminfo(vmname)))
#     if not vminfo(vmname)=='running':
#         run("virsh start %s" % vmname)

# def shutdown_vm(vmname):
#     if not vminfo(vmname)=='shut off':
#         run("virsh shutdown %s" % vmname)
    
# @task
# @roles('updateimg')
# @parallel
# def hv_prepareimg():
#     '''prepare img on the HV where set in file host node [updateimg]
#         it will prepare a LV in 5G for the vm img to store
#         if there is already have a lv called /dev/vg/ostemplet
#         it will be rebuild 
#         Arguments:
#         cntempleturl:    the folder where store templet img on the CN 
#         hvtempleturl:    the folder where store templet img on the HV
#         vgapp:           the vg on the HV which you want to create lv for img on
#     '''
#     cntempleturl = cfg_vars["cntemplet_url"]
#     hvtempleturl = cfg_vars["mount_ostemplet"]
#     vgapp = cfg_vars["vg_name"]
#     file_items = cfg_vars["file_items"]
#     unzip_imgs = cfg_vars["unzip_imgs"]
#     ostemplet_lv_size = cfg_vars["ostemplet_lv_size"]
#     lv_name = cfg_vars["lv_name"]

#     execute(_get_img_to_hv_,cntempleturl,hvtempleturl,vgapp,file_items.split(","),unzip_imgs.split(","),ostemplet_lv_size,lv_name)



# @task
# @roles('lvextend')
# @parallel
# def vm_start():
#     '''start vm  on the HV where set in file host node [startvm]'''
#     #修改fstab
#     #nano /etc/fstab

#     #重启
#     #运行两句命令

#     #e2fsck -f /dev/vg_vmapp/lvapp
#     #python /root/lvextend.py
#     if(env.host_string==None):
#         return
#     if(env.host_string.find("@")):
#         if(env.host_string.find(".")):
#             hvname=env.host_string[env.host_string.find("@")+1:env.host_string.find(".")]
#         else:
#             hvname=env.host_string[env.host_string.find("@")+1:len(env.host_string)]
#     else:
#         hvname=env.host_string
#     vms=[]
#     global startvmlist
#     global hostsiplist
#     global hostsnetworklist
#     for v in startvmlist:
#         if 'root@'+str(v[0])==env.host_string:
#             vms.append(v[1])

#     for v in vms:
#         vmname=v.split('.')[0]
#         start_vm(vmname)