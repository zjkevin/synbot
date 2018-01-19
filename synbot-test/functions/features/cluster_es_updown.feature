# -*- coding: utf-8 -*-

Feature: elasticsearch的安装和启停
    Background
        Given: 存在测试集群, SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在elasticsearch
        Given: 目标集群{}中目标虚拟机组{}上的elasticsearch服务状态为关闭    

    Scenario: synbot启动目标机虚拟机中的elasticsearch
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/es/es_start.yml
        """
        Then 目标虚拟机组{}elasticsearch服务状态为启动

    Scenario: synbot关闭目标机虚拟机中的elasticsearch
        Given: 启动目标集群{}中目标虚拟机组{}上的elasticsearch服务
        Given: 目标集群{}中目标虚拟机组{}上的elasticsearch服务状态为启动        
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/es/es_stop.yml
        """
        Then 目标虚拟机组{}elasticsearch服务状态为关闭

    Scenario: synbot重启目标机虚拟机中的elasticsearch
        Given: 启动目标集群{}中目标虚拟机组{}上的elasticsearch服务
        Given: 目标集群{}中目标虚拟机组{}上的elasticsearch服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/es/es_restart.yml
        """
        Then 目标虚拟机组{}elasticsearch服务状态为启动

    Scenario: synbot重启目标机虚拟机中的elasticsearch
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/es/es_restart.yml
        """
        Then 目标虚拟机组{}elasticsearch服务状态为启动