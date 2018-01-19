# -*- coding: utf-8 -*-

Feature: zookeeper的安装和启停

    Scenario: synbot向目标机虚拟机中安装zookeeper
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/zk/zk_install.yml -e zkc=zookeeper
        """
        Then 检查zk配置文件符合text中的描述
        """
            
        """ 

    Scenario: synbot启动目标机虚拟机中的zookeeper
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在zookeeper
        Given: 目标集群{}中目标虚拟机组{}上的zookeeper服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/zk/zk_start.yml -e zkc=zookeeper
        """
        Then 目标虚拟机组{}zookeeper服务状态为启动

    Scenario: synbot关闭目标机虚拟机中的zookeeper
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在zookeeper
        Given: 目标集群{}中目标虚拟机组{}上的zookeeper服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/zk/zk_stop.yml -e zkc=zookeeper
        """
        Then 目标虚拟机组{}zookeeper服务状态为关闭

    Scenario: synbot重启目标机虚拟机中的zookeeper
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在zookeeper
        Given: 目标集群{}中目标虚拟机组{}上的zookeeper服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/zk/zk_restart.yml -e zkc=zookeeper
        """
        Then 目标虚拟机组{}zookeeper服务状态为启动

    Scenario: synbot重启目标机虚拟机中的zookeeper
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在zookeeper
        Given: 目标集群{}中目标虚拟机组{}上的zookeeper服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/zk/zk_restart.yml -e zkc=zookeeper
        """
        Then 目标虚拟机组{}zookeeper服务状态为启动  