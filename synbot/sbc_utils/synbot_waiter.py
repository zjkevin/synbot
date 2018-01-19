#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie
import yaml
import sbc_context
from fabric.colors import *
import synbot_conf_utils
import synbot_group_vars
import synbot_hosts
import synbot_tools

def print_help_menu():
    with open(sbc_context.get_config_files()["HELP_MENU_FILE"], 'rb') as f:
        d = yaml.load(f)
        for i in d["helps"]:
          print green(i["kind"].center(80,"*"))
          if i.has_key("cmds"):
            for x in i["cmds"]:
              print synbot_tools.str_newline(yellow(x["cmd"]) + "  " + green(x["content"]).strip(),80,4)
          if i.has_key("flows"):
            for x in i["flows"]:
              content = ""
              print synbot_tools.str_newline(yellow(x["title"]), 80, 4)
              for i,c in enumerate(x["content"].split("|")):
                if i == len(x["content"].split("|")) - 1:
                  content = content + green(c)
                else:
                  content = content + green(c) + " " + cyan("-->") + " "
              print " "*4 + content

def get_cmds_list():
    cmds_list = []
    with open(sbc_context.get_config_files()["HELP_MENU_FILE"], 'rb') as f:
      d = yaml.load(f)
      for i in d["helps"]:
        if i.has_key("cmds"):
          for x in i["cmds"]:
            cmds_list.append(x["cmd"])
    return cmds_list  