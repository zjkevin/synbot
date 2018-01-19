# -*- coding: utf-8 -*-

Feature: hbase的安装和启停

    Scenario: synbot向目标机虚拟机中安hbase
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        when 向synbot提交text中描述的hosts文件
        """
            [hbase_master]
            p2n1
            [hbase_hdfs]
            p2n1
            [hbase_regionserver]
            p2n1
            p2n2
            p2n3
            
            [hbase_zk]
            p2n1
            p2n2
            p2n3
            [hbase:children]
            hbase_master
            hbase_regionserver
        """       
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/hbase/hbase_install.yml
        """
        Then 检查hbase配置文件符合text中的描述
        """
            
        """ 

    Scenario: synbot启动目标机虚拟机中的hbase
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hbase集群
        """
            [hbase_master]
            p2n1
            [hbase_hdfs]
            p2n1
            [hbase_regionserver]
            p2n1
            p2n2
            p2n3
            
            [hbase_zk]
            p2n1
            p2n2
            p2n3
            [hbase:children]
            hbase_master
            hbase_regionserver
        """
        Given: 目标集群中hbase集群服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/hbase/hbase_start.yml
        """
        Then 目标集群中hbase集群服务状态为启动


    Scenario: synbot关闭目标机虚拟机中的hbase
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hbase集群
        """
            [hbase_master]
            p2n1
            [hbase_hdfs]
            p2n1
            [hbase_regionserver]
            p2n1
            p2n2
            p2n3
            
            [hbase_zk]
            p2n1
            p2n2
            p2n3
            [hbase:children]
            hbase_master
            hbase_regionserver
        """
        Given: 目标集群中hbase集群服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/hbase/hbase_stop.yml
        """
        Then 目标集群中hbase集群服务状态为关闭

    Scenario: synbot重启目标机虚拟机中的hbase
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hbase集群
        """
            [hbase_master]
            p2n1
            [hbase_hdfs]
            p2n1
            [hbase_regionserver]
            p2n1
            p2n2
            p2n3
            
            [hbase_zk]
            p2n1
            p2n2
            p2n3
            [hbase:children]
            hbase_master
            hbase_regionserver
        """
        Given: 目标集群中hbase集群服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/hbase/hbase_restart.yml
        """
        Then 目标集群中hbase集群服务状态为启动

    Scenario: synbot重启目标机虚拟机中的hbase
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hbase集群
        """
            [hbase_master]
            p2n1
            [hbase_hdfs]
            p2n1
            [hbase_regionserver]
            p2n1
            p2n2
            p2n3
            
            [hbase_zk]
            p2n1
            p2n2
            p2n3
            [hbase:children]
            hbase_master
            hbase_regionserver
        """
        Given: 目标集群中hbase集群服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/hbase/hbase_restart.yml
        """
        Then 目标集群中hbase集群服务状态为启动