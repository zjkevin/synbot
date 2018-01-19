#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from fabric.api import run, execute, put, settings, cd ,local ,task,env,roles,get,hide
from fabric.colors import *

def prepareimg(updateflag,cntempleturl,hvtempleturl,file_items,unzip_imgs):
    '''propre img on the remote host'''

    with settings(warn_only=True),hide("output"),hide("warnings"):
        for v in file_items:
            if updateflag :
                put("%s/%s" % (cntempleturl,v) , "%s/%s" % (hvtempleturl,v))
            else :
                if run("test -e %s/%s" % (hvtempleturl,v)).failed:
                    put("%s/%s" % (cntempleturl,v) , "%s/%s" % (hvtempleturl,v))         
                    
        for v in unzip_imgs:
            if run("test -e %s/%s" % (hvtempleturl,v)).failed:
                with cd(hvtempleturl):
                    run("tar -xzmvf %s/%s.tar.gz" % (hvtempleturl,v))

def updateimg():
    prepareimg(True)


if __name__ == '__main__' :
    prepareimg(False)
