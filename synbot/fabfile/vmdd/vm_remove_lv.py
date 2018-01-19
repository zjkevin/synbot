#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,hide
from fabric.colors import *

import utils

def removevmlv(hostname):
    '''remove vm lv on the remote host'''
    with settings(warn_only=True),hide("output"):
        run("virsh destroy %s" % hostname)
        run("virsh undefine %s" % hostname)
        ret = run("lvs")
        ret_list = ret.split("\n")
        for l in ret_list:
            _vg = ''
            _lv = ''
            if l.strip().startswith(hostname+"_") or l.strip().startswith(hostname+"os") or l.strip().startswith(hostname+"swap"):
                temp = l.strip().split(" ")
                temp_list = [i for i in temp if i != '']
                _lv = temp_list[0]
                _vg = temp_list[1]
                print(cyan(temp_list))
                print(cyan(_lv))
                print(cyan(_vg))
                if _lv != '' and _vg != '':
                    print(cyan("remove /dev/%s/%s..." %(_vg,_lv)))
                    run("lvchange -a n /dev/%s/%s" % (_vg,_lv))
                    run("lvremove /dev/%s/%s" % (_vg,_lv))
                else:
                    print(green("there is no lv named /dev/%s/%s need remove" %(_vg,_lv)))
                    print(cyan(temp_list))
                    print(cyan(_lv))
                    print(cyan(_vg))