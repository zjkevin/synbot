#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import os
import sys

import yaml
import codecs
import logging
import logging.config
from fabric.colors import *

import synbot_env
from sbc_module import synbot_network
from sbc_module import synbot_clusterconf
from sbc_module import synbot_clusterstartstop
from sbc_module import synbot_clusterinstall
from sbc_module import synbot_info
from sbc_module import synbot_mem
from sbc_module import synbot_disk
from sbc_module import synbot_vm
from sbc_module import synbot_hv
from sbc_module import synbot_setting
from sbc_utils import synbot_tools
from sbc_utils import sbc_context
from sbc_utils import synbot_waiter

_RETRY = 12
#-vmclear 'clear vm on the HV "sbc -vmclear poc1,poc[4~8]"'
#************************ hardware ************************
#-scanpv 'scan pv on HV, default scan [mother_land] in hosts, or "sbc -scanpv poc1,poc[4~8]"'
#-scandisk 'scan disk on HV, default scan [mother_land] in hosts, or "sbc -scandisk poc1,poc[4~8]" scan results will be stored in ./cluster_config/scan_disk.yml'   
#-scanmem 'scan mem for hosts'
#-mountdisk 'mount disk depend on cluster define yml'
#-img 'update VirtualMachine img to HV'  
#-s  'sources status'

os.chdir(os.environ["SYNBOT_HOME"])

with codecs.open('./conf/logging.yaml', 'r', 'utf-8') as logging_file:
  logging.config.dictConfig(yaml.load(logging_file))

_logger = logging.getLogger(__name__)


#DEBIAN_SOURCE_MOUNT_POINT = '/var/www/deb71amd64/'
#DEB_LOG_DIR = '/var/log/deb_source_server.log'
#PIP_LOG_DIR = '/var/log/pip_source_server.log'

class cluster_config(object):
  """docstring for cluster_config"""
  def __init__(self):
    super(cluster_config, self).__init__()
  host_list = zk_host_list = hive_host_list = spark_host_list = []  
  hadoop_namenode = hadoop_datanode = hadoop_journalnode = hadoop_resource_manager = hadoop_history_job_manager = []
  hbase_master = hbase_regionserver = storm_master = storm_slave = es_host_list = []
  esc_name = "es_default_name"    
  web_node = ""
  cluster_data_none_config = {}
  vm_list = []

##检查集群配置
#def __check_cluster_config(**arg):
#    sbcenv = synbot_env.get_synbot_ini()
#    modules = sbcenv.cluster_modules
#    print "check cluster config file for this cluster"

#创建集群定义文件
#def __define_cluster_config(**arg):
#    sbcenv = synbot_env.get_synbot_ini()
#    try:
#      if len(arg["args"]) == 0:
#        print red("missing config file name, please use 'sbc -d <config_file>' to define it")
#        sys.exit(0)
#      #非空
#      path = arg["args"][0].strip()
#      if path == "":
#        print red("path must be set")
#        sys.exit(0)
#      #后缀
#      if path.find(".") == -1:
#        path = path + ".yml"
#      else:
#        if path.split(".")[-1] not in ("yml","yaml"):
#          path = path + ".yml"
#      #文件
#      if path.find("/") == -1:
#        if sbcenv.cluster_config_path == "" or sbcenv.cluster_config_path == None:
#          sbcenv.cluster_config_path = "/".join(sys.argv[0].split("/")[0:-1]) + "/cluster_config"
#        path = sbcenv.cluster_config_path + "/" + path
#      else:#路径
#        if os.path.exists(path):
#          if os.path.isfile(path):
#            raw_input_validate = raw_input("this file is exist are you sure to reload it?(yes/no)")
#            if raw_input_validate.lower() not in ("yes","y"):
#              sys.exit(0)
#          else:
#            print red("it seems the path:%s is a dir not a file you can not rewrite it" % path)
#            sys.exit(0)
#        if path.split("/")[-1] in (".yml",".yaml"):
#          print red("the file must have a name '%s'" % path)
#          sys.exit(0)
#      if not os.path.exists("/".join(path.split("/")[0:-1])):
#         os.makedirs("/".join(path.split("/")[0:-1]))
#      #exit
#      if os.path.exists(path):
#        create_validate = raw_input(red("this config file is exit! do you want switch to this config file?(yes/no)"))
#        if create_validate.lower() not in ("yes","y"):
#          sys.exit(0)
#        else:
#          print green("switch config file to path:%s success!" % path)
#      else:
#        __cluster_conf_file = None
#        if sbcenv.base == "hv":
#          __cluster_conf_file = CLUSTER_CONF_TEMPLET_HV_FILE
#        else:
#          __cluster_conf_file = CLUSTER_CONF_TEMPLET_VM_FILE
#        open(path,"w").write(open(__cluster_conf_file,"r").read())
#        print green("create config file to path:%s success!" % path)
#      
#      #写回配置文件
#      sbcenv.cluster_config_file = path.split("/")[-1]
#      sbcenv.cluster_config_path = "/".join(path.split("/")[0:-1])
#      synbot_env.set_synbot_ini(sbcenv)      
#    except Exception, e:
#        print red("create config error:%s" % e)

#设置集群配置文件目录
#def __set_config_file_path(**arg):
#    try:
#      sbcenv = synbot_env.get_synbot_ini()
#      if len(arg["args"]) == 0:
#        if sbcenv.cluster_config_path.strip() == "":
#          print red("config path has not been set yet, please use 'sbc -p <path>' to set it")
#        else:
#          print cyan("the config path now is been set to: '%s'" % sbcenv.cluster_config_path)
#        if sbcenv.cluster_config_file.strip() == "":
#          print red("config file has not been set yet, please use 'sbc -d <config_file>' to define it")
#        else:
#          print cyan("current config file is : '%s/%s'" % (sbcenv.cluster_config_path , sbcenv.cluster_config_file))
#        sys.exit(0)
#      path = arg["args"][0].strip()
#      if os.path.isfile(path):
#        print red("the path is a file,you must input a dir")
#        sys.exit(0)
#      else:
#        if not os.path.exists(path):
#          raw_input_validate = raw_input("this path is not exist do you want to create it?(yes/no)")
#          if raw_input_validate.lower() not in ("yes","y"):
#            sys.exit(0)
#          else:
#            os.makedirs(path)
#        sbcenv.cluster_config_path = path
#        #写回配置文件
#        synbot_env.set_synbot_ini(sbcenv)
#        print green("the config path is been set to: '%s'" % sbcenv.cluster_config_path)
#    except Exception, e:
#        print red("set config path error:%s" % e)

#def __edit_network_config_file(**arg):
#    sbcenv = synbot_env.get_synbot_ini()
#    if sbcenv.base == "vm":
#      os.system("vim conf/network_conf_vm.yml")
#    else:
#      os.system("vim conf/network_conf_hv.yml")

#def __debian_source(**arg):
#    sbcenv = synbot_env.get_synbot_ini()
#    __debian_source_host = sbcenv.sources["debian_source_host"]
#    __debian_source_port = sbcenv.sources["debian_source_port"]
#    __debian_source_iso = sbcenv.sources["debian_source_iso"]
#    try:
#      opts,args = getopt.getopt(arg["args"], "s:i:p:",["host=","iso_dir=","port="])
#      print opts
#      for item in opts:
#        print item
#        if item[0] == "-s" or item[0] == "--host":
#          __debian_source_host = item[1]
#        if item[0] == "-i" or item[0] == "--iso_dir":
#          __debian_source_iso = item[1]
#        if item[0] == "-p" or item[0] == "--port":
#          __debian_source_port = item[1]
#      synbot_env.set_synbot_ini(sbcenv)
#      synbot_source.deploy_debian(__debian_source_iso,__debian_source_host,__debian_source_port,mount_point=DEBIAN_SOURCE_MOUNT_POINT,log_dir=DEB_LOG_DIR)
#      #print args
#    except getopt.GetoptError as ex:
#      print ex

#def __pip_source(**arg):
#    sbcenv = synbot_env.get_synbot_ini()
#    __pip_source_host = sbcenv.sources["pip_host"]
#    __pip_source_dir = sbcenv.sources["pip_source"]
#    __pip_source_port = sbcenv.sources["pip_port"]
#    try:
#      opts,args = getopt.getopt(arg["args"], "s:d:p:",["host=","pip_dir=","port="])
#      print opts
#      for item in opts:
#        print item
#        if item[0] == "-s" or item[0] == "--host":
#          __pip_source_host = item[1]
#        if item[0] == "-d" or item[0] == "--pip_dir":
#          __pip_source_dir = item[1]
#        if item[0] == "-p" or item[0] == "--port":
#          __pip_source_port = item[1]
#      synbot_env.set_synbot_ini(sbcenv)
#      synbot_source.deploy_pip(__pip_source_dir,__pip_source_host,__pip_source_port,log_dir=PIP_LOG_DIR)
#      #print args
#    except getopt.GetoptError as ex:
#      print ex

if __name__=="__main__":
    #arg_parser = argparse.ArgumentParser()
    #arg_parser = argparse.ArgumentParser()
    #arg_parser.add_argument('-n', '--nfs', required=True, help="nfs list string list this:192.168.110.187:/home/hadoop/nfstest,192.168.1.1:/home/hadoop/nfs1,192.168.1.2:/home/hadoop/nfs2,192.168.1.2:/home/hadoop/nfs3", type=str)
    #parser_args = arg_parser.parse_args()
    #nfs_mount_check(parser_args.nfs)
    sbc_context.set_sbt_env(synbot_env.get_synbot_ini())
    cmds_list = synbot_waiter.get_cmds_list()
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] in ("--help","-h")):
      synbot_waiter.print_help_menu()
      sys.exit(0)
    elif len(sys.argv) > 1 and (sys.argv[1] in cmds_list or "-hide" in sys.argv):
      def calf(type,**arg):
        result = {"-i":lambda:synbot_clusterinstall.install_cluster(**arg),
                "-i-all":lambda:synbot_clusterinstall.install_all_cluster(**arg),
                "-rebuild":lambda:synbot_clusterinstall.rebuild_cluster(**arg),
                "-rebuild-all":lambda:synbot_clusterinstall.rebuild_all_cluster(**arg),
                "-restart":lambda:synbot_clusterstartstop.restart_cluster(**arg),
                "-start":lambda:synbot_clusterstartstop.start_cluster(**arg),
                "-stop":lambda:synbot_clusterstartstop.stop_cluster(**arg),
                "-d":lambda:synbot_clusterconf.define_cluster_config(**arg),
                "-p":lambda:synbot_clusterconf.set_config_file_path(**arg),
                "-e":lambda:synbot_clusterconf.edit_config_file(**arg),
                "-s":lambda:synbot_info.check_sources(**arg),
                "-cn":lambda:synbot_info.get_cn_info(**arg),
                "-parse":lambda:synbot_clusterconf.parse_cluster_config(**arg),
                "-img":lambda:synbot_hv.update_img_for_hv(**arg),
                "-hv":lambda:synbot_hv.hv_init(**arg),
                "-scanpv":lambda:__scan_pv(**arg),
                "-scandisk":lambda:synbot_disk.scan_disk(**arg),
                "-ssh":lambda:synbot_network.ssh_dispense(**arg),
                "-ping":lambda:synbot_network.ping_host(**arg),
                "-socket":lambda:synbot_network.socket_host(**arg),
                "-createhosts":lambda:synbot_network.create_hosts(**arg),
                "-sendhosts":lambda:synbot_network.send_hosts(**arg),
                "-en":lambda:synbot_network.edit_network_config_file(**arg),
                "-vmclear":lambda:synbot_vm.vm_clear(**arg),
                #"-debiansource":lambda:__debian_source(**arg),
                #"-pipsource":lambda:__pip_source(**arg),
                "-scanmem":lambda:synbot_mem.scan_mem(**arg),
                #"-zk":lambda:synbot_zk.zk_install(**arg),
                "-hvmode":lambda:synbot_setting.change_mode("hv"),
                "-vmmode":lambda:synbot_setting.change_mode("vm"),
                "-diskformat":lambda:synbot_disk.format_disk(**arg),
                "-diskmount":lambda:synbot_disk.mount_disk(**arg)
                }
        result[type]()
      sbcenv = sbc_context.get_sbt_env()
      sbcenv.cluster_username = 'hadoop'
      sbc_context.set_sbt_env(sbcenv)
      print yellow("synbot base information start".center(80,"-"))
      print yellow("mode:%s" % sbcenv.base)
      if sbcenv.cluster_config_path == "" and sbcenv.cluster_config_file == "":
        print yellow("current config file: no set")
      else:
        print yellow("current config file:%s" % synbot_tools.path_join(sbcenv.cluster_config_path,sbcenv.base,sbcenv.cluster_config_file))
      if sbcenv.base == "vm":
        print yellow("network config file:%s" % synbot_tools.path_join(os.path.abspath("."),"conf/network_conf_vm.yml"))
      else:
        print yellow("network config file:%s" % synbot_tools.path_join(os.path.abspath("."),"conf/network_conf_hv.yml"))
      print yellow("synbot base information end".center(80,"-"))
      args_list = sys.argv
      if "-hide" in args_list:
        args_list.remove("-hide")
      calf(args_list[1],args=args_list[2:])                
    else:
      print("Try `sbc --help' for more information.")
      sys.exit(0)