#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

import os
import synbot_tools

ALL_FILE = HOSTS_FILE = synbot_tools.current_file_directory() + "/../group_vars/all"

def edit_group_vars_all(config_all_change_dict):
    f = open(ALL_FILE, 'r')
    lines = f.readlines()
    f.close()
    f = open(ALL_FILE, 'w')
    for l in lines:
      if ":" in l and l.split(":")[0] in config_all_change_dict.keys():
        f.write("%s: %s\n" % (l.split(":")[0],config_all_change_dict[l.split(":")[0]]))
      else:
        f.write("%s\n" % l.strip())
    f.close()

if __name__ == '__main__':
    edit_group_vars_all({"current_mem":"18"})
