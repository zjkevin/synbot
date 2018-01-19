#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from ConfigParser import SafeConfigParser as __scfgp
import os, sys, re, StringIO,threading,signal
from fabric.colors import *
import yaml

_setv_pmpt ='"%s" not set, please set it: '

def exit_info(info):
    print info
    sys.exit(1)
    
def exit_onoe(path):
    if not os.path.exists(path):
        print '"%s" file not found. Bye, Sir.' % path
        sys.exit(1)

def ensure_input(pnm,pval):
    pval = pval or raw_input(_setv_pmpt % pnm) or None
    if not pval:
        print '''No idea what to do if you don't set "%s". Bye, Sir.''' % pnm
        sys.exit(1)
    return pnm,pval

def ensure_inputEx(pnm,pval,prompt,regex,sample,forceFailExit=False,failValue=None):
    '''ensure input with default value show and regular expression verify.'''
    failedResult = (pnm,failValue)    
    if not pnm :
        print "Invalid <pnm> in ensure_inputEx() call,please set it first."
        if forceFailExit :
            sys.exit(1);
        else:
            return failedResult
    if not regex and not sample :
        print "Invalid <sample> in ensure_inputEx() call,please set it first." 
        if forceFailExit :
            sys.exit(1);
        else:
            return failedResult
    if not prompt : prompt = pnm
    if not regex : regex = "\\S+"
    pattern = re.compile(regex)
    if pval : 
        input = raw_input('default <%s> is <%s>, ENTER for DEFAULT.\n<%s>:' % (prompt,pval,prompt))
        while (input and not pattern.match(input)) :
            input = raw_input('Invalid <%s>,example:<%s>, ENTER for DEFAULT!\n<%s>:'  % (prompt,sample,prompt))
        if not input :
            input = pval
            print ('<%s>:<%s>'  % (prompt,pval))
    else :
        input = raw_input('Please input <%s> as <%s> ,ENTER to CANCEL.\n<%s>:' % (prompt,sample,prompt))
        #input = raw_input('%s=%s(%s),<ENTER> to CANCEL:\n %s:' % (pnm,pval,prompt,pnm))
        while (input and not pattern.match(input)) :
            #input = raw_input('Please set <%s> as <%s>,<ENTER> to CANCEL!' % (pnm,sample))
            input = raw_input('Invalid <%s>,example:<%s>, <ENTER> to CANCEL.\n<%s>:'  % (prompt,sample,prompt))
        if not input :
            print '''<%s> NOT set, process was cancelled.''' % prompt
            if forceFailExit :
                sys.exit(1);
            else:
                return failedResult
    return (pnm,input)

def load_vars(**var_defaults):
    'Read variable config files and return values of vars specifed by var_defaults. If no any var_defaults specified, return all configured vars.'
    if not os.path.exists('group_vars/all'):
        return var_defaults
    cfg = __scfgp(allow_no_value=True)
    fake_head = 'nlj2n086bg88tu'
    with open('group_vars/all', 'rb') as f:
        cfg.readfp(StringIO.StringIO(u'[%s]\n%s' %(fake_head, f.read())))
    cfg_vars = dict(cfg.items(fake_head))
    if var_defaults:
        kvs = [(k, v if v is not None else cfg_vars.get(k,v)) for k,v in var_defaults.items()]
        kvs = [(k, v or raw_input(_setv_pmpt % k)) for k,v in kvs]
        kvs = [(k, v.strip() if v else None) for k,v in kvs]
        return dict(kvs)
    else:
        return cfg_vars

def load_hosts(cluster):
    '''Read configure files(complied with Ansible), return a list of 2-tuples as (p_domain, v_domain) of nodes in the arg "cluster", while p_domain is the domain name of the physical machine on which the vm of v_domain resides. If the "cluster" is a full domain name, return (None, cluster) directly.'''
    if re.match(r'^\w+\.\w+(\.\w+)*$', cluster):
        return None, cluster
    cfg = __scfgp(allow_no_value=True)
    hosts_path = 'hosts'
    exit_onoe(hosts_path)
    cfg.read(hosts_path)
    var_defaults = [('physical_cluster', 'mother_land'), 
                    ('default_domain',   'dev.s'),
                    ('pnm_rgx',  r'^[^\d]+(\d+)$'),
                    ('vnm_rgx',  r'^[^\d]+(\d+)[^\d]+(\d+)$'),]
    cfg_vars = load_vars(**dict(var_defaults))
    pcluster, domain, pnm_rgx, vnm_rgx = map(lambda x:cfg_vars[x[0]], var_defaults)
    if not cfg.has_section(pcluster):
        print 'Physical cluster "%s" not defined in file "%s", please define it first.' % (pcluster, hosts_path)
        sys.exit(1)
    phy_nodes = cfg.options(pcluster)
    def fig_phynode(vm):
        vm_mch = re.match(vnm_rgx, vm.split('.')[0])
        if not vm_mch:
            return None,vm
        mch_ps = [(re.match(pnm_rgx, p.split('.')[0]), p) for p in phy_nodes]
        idx_ps=[(m.groups()[0], p) for m,p in mch_ps if m]
        return next((p for pidx, p in idx_ps if vm_mch.groups()[0]==pidx), None), vm
    if cluster==pcluster:
        p_vms = zip(phy_nodes, phy_nodes) #if it's the physical cluster, let's comply with the return spec.
    else:
        if cfg.has_section(cluster):
            p_vms = [fig_phynode(vm) for vm in cfg.options(cluster)]
        else:
            p_vms=[fig_phynode(cluster)]
    return [map(lambda x: x and ((('.' in x) and x) or '%s.%s'%(x,domain)), p_vm) for p_vm in p_vms]

def __sighdn_wrapper(exit_flg):
    def _sighdn_exit(x,y):
        print 'Task can NOT be interrupted, CTRL+C ingnored.'
        exit_flg.set()
    return _sighdn_exit

def ignore_ctrl_c():
    exit_flg = threading.Event()
    signal.signal(signal.SIGINT, __sighdn_wrapper(exit_flg))

def load_hostsip_config():
    '''load config file of hostscfg'''
    hostsnetworklist={}
    vg_conf_dict = {}
    hostsiplist={}
    diskextslist={}
    
    f_network_conf = open('conf/network_conf_hv.yml','r')
    f_network_conf_dict = yaml.load(f_network_conf)
    for ip_blk in f_network_conf_dict["ipaddress_block"]:
        hostsnetworklist[ip_blk["ipaddress_prefix"]] = '%s.* %s %s %s %s' % (ip_blk["ipaddress_prefix"],ip_blk["netmask"],ip_blk["network"],ip_blk["gateway"],ip_blk["nameserver"])
    f_network_conf.close()

    f_temp = open('cluster_config/cluster_ip.yml','r')
    hostsiplist = yaml.load(f_temp)
    hostsiplist = hostsiplist["ipaddress"]
    f_temp.close()

    f_vg_conf = open('conf/vg_conf.yml','r')
    f_vg_conf_dict = yaml.load(f_vg_conf)
    for (k,v) in f_vg_conf_dict.items():
        vg_conf_dict[k] = v
    f_vg_conf.close()

    config={}
    config.setdefault('hostsnetworklist',hostsnetworklist)
    config.setdefault('vg_conf',vg_conf_dict)  
    config.setdefault('hostsiplist',hostsiplist)
    config.setdefault('diskextslist',load_cluster_disk_config_yaml()) 
    return config

def load_cluster_disk_config_yaml():
    diskextslist = {}
    cluster_disk_config_yaml = None
    if os.path.exists('cluster_config/cluster_disk_config.yml'):
        f = open('cluster_config/cluster_disk_config.yml','r')
        cluster_disk_config_yaml = yaml.load(f)
        f.close()
    if not cluster_disk_config_yaml == None:
        for (k,v) in cluster_disk_config_yaml.items():
            diskextslist.setdefault(k,__disk_config_dict(v))
    return diskextslist

def __disk_config_dict(config):
    ret_config = []
    for cfg in config:
        size = ""
        if cfg.has_key("size"):
            if cfg["size"].lower().endswith("g"):
                size = cfg["size"]
            else:
                print red("disk size unit must be 'g', use 'sbc -e' to check")
                sys.exit(0)
        if cfg["name"] in synbotenv.APP_DISK_INDEX.keys():
            vgapp = cfg["vg"] if cfg.has_key("vg") else "vgapp"
            ret_config.append({"name":cfg["name"],"info":{"vg":"%s" % vgapp,"size":"%s" % size,"pvs":"%s" % cfg["disk"]}})
    return ret_config

def __disk_config(hostname,config):
    config_list = []
    ret_config = []
    if "," in config:
        config_list = config.split(",")
    else:
        config_list.append(config)
    for cfg in config_list:
        cfg_item = str(cfg).split("|")
        vgapp = "vgapp"
        if len(cfg_item) == 4:
            vgapp = cfg_item[3]
        if len(cfg_item) ==3 or len(cfg_item) ==4:
            if cfg_item[0] in synbotenv.APP_DISK_INDEX.keys() and cfg_item[2].endswith("G"):
                ret_config.append({"name":cfg_item[0],"info":{"vg":"%s" % vgapp,"size":"%s" % cfg_item[2],"pvs":"%s" % cfg_item[1]}})
    return ret_config

class synbotenv(object):
    """docstring for env"""
    def __init__(self, arg):
        super(env, self).__init__()
        self.arg = arg

    DISK_SYMBOL = ['c','d','e','f','g','h','i','j','k','l','m','n','o','p','q'\
                  'r','s','t','u','v','w','x','y','z']

    APP_DISK_INDEX = {"es":0,"dn":0,"log":0,"tmp":0,"nn":0,"zk":0,"jn":0} 

if __name__ == "__main__":
   load_hostsip_config()
        