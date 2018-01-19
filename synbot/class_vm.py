#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#author zhangjie

class VirtualMachine(object):
    """docstring for VirtualMachine"""
    def __init__(self,name):
        super(VirtualMachine, self).__init__()
        self.__name = name
        
    __name = ""
    __mem = 1
    __current_mem = 1
    __vcpu = 1
    __swap_size = "1G"
    __disk_list = []

    #geter seter
    def getname(self):
        return self.__name

    def setname(self,value):
        self.__name = value    

    def getmem(self):
        return self.__mem

    def setmem(self,value):
        self.__mem = value

    def getcurrent_mem(self):
        return self.__current_mem

    def setcurrent_mem(self,value):
        self.__current_mem = value

    def getvcpu(self):
        return self.__vcpu

    def setvcpu(self,value):
        self.__vcpu = value

    def getswap_size(self):
        return self.__swap_size

    def setswap_size(self,value):
        self.__swap_size = value


class VMDisk(object):
    """docstring for VMDisk"""
    def __init__(self):
        super(VMDisk, self).__init__()

    __mount = ""
    __name = ""
    __disk_logic_name = ""
    __pvs = []
    __size = ""
        
    #geter seter
    def getmount(self):
        return self.__mount

    def setmount(self,value):
        self.__mount = value

    def getname(self):
        return self.__name

    def setname(self,value):
        self.__name = value

    def getdisk_logic_name(self):
        return self.__disk_logic_name

    def setdisk_logic_name(self,value):
        self.__disk_logic_name = value

    def getpvs(self):
        return self.__pvs

    def setpvs(self,value):
        self.__pvs = value

    def getsize(self):
        return self.__size

    def setpvs(self,value):
        self.__size = value


