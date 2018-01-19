#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

import ConfigParser

#增加一个配置项设定值，如存在则更新
def addupdate_config_file_item(config_file,section,confitem,value):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    if section not in config.sections():
      config.add_section(section)
    config.set(section,confitem,value)
    config.write(open(config_file,"w"))

#删除配置文件项
def remove_config_section(config_file,section):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    config.remove_section(section)
    config.write(open(config_file,"w"))

#修改配置节点项
def edit_config_file(config_file,section,configs):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    config.remove_section(section)
    config.add_section(section)
    for c in configs:
        config.set(section,c)
    config.write(open(config_file,"w"))

#修改配置节点项值
def edit_config_file_item(config_file,section,confitem,value):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    if section not in config.sections():
      config.add_section(section)
    config.set(section,confitem,value)
    config.write(open(config_file,"w"))

#重命名配置文件项
def rename_config_section(config_file,section_oldname,section_newname):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    if section_oldname in config.sections():
        config.add_section(section_newname)
        for c in config.options(section_oldname):
            config.set(section_newname,c)
        config.remove_section(section_oldname)
    config.write(open(config_file,"w"))

#得到一个配置项的值
def get_config_file_item(config_file,section,confitem):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    if section not in config.sections():
      return None
    return config.get(section,confitem)

#得到配置节点的所有属性
def get_config_file_options(config_file,section):
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    if section not in config.sections():
      return None
    return config.options(section)

#还未实现，暂时不用
#实现功能 k1.k2.k3 = 1 转化为dict {"k1":{"k2":{"k3":1}}}
def conf_parse():
    conf_file = open("/root/xxx.ini","r")
    lines = conf_file.readlines()
    conf_file.close()
    return_dict = {}
    c = 0
    def _get_dic(k,v,c,r_dict):
        print("%s:%s.%s" % (k,v,c))
        c = c + 1
        if "." in k:
            _ks = k.split(".")
            print yellow(_ks)
            if r_dict.has_key(_ks[0]):
                r_dict.update({_ks[0]:_get_dic(".".join(_ks[1:]),v,c,r_dict)})
            else:
                r_dict[_ks[0]] = _get_dic(".".join(_ks[1:]),v,c,r_dict)
        else:
            r_dict[k] = v
        return r_dict

    for l in lines:
        l = l.strip()
        if "=" in l:
            k = l.split("=")[0]
            v = l.split("=")[1]
        if "." in k:
            ks = k.split(".")
            _index = 0
            for k in ks[0:-1]:
                if not return_dict.has_key(k):
                    return_dict[k] = {}
            # return_dict[][][]
            # if return_dict.has_key(ks[0]):
            #     return_dict.update({ks[0]:_get_dic(".".join(ks[1:]),v,c,return_dict)})
            # else:
            #     return_dict[ks[0]] = _get_dic(".".join(ks[1:]),v,c,return_dict)
        else:
            return_dict[k] = v
    print cyan(return_dict)

if __name__ == "__main__":
    pass
    #print get_hosts_config_sec("mother_land")
    #print get_hosts_config_sec("zookeeper")
    #update_etc_hosts([])
    #conf_parse()