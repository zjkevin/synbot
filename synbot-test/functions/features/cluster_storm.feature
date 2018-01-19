# -*- coding: utf-8 -*-

Feature: storm的安装和启停

    Scenario: synbot向目标机虚拟机中安装storm
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        when 向synbot提交text中描述的hosts文件
        """
            [hdfs_nn]
            p2n1
            [hdfs_rm]
            p2n1
            [hdfs_hm]
            p2n1
            [hdfs_dn]
            p2n1
            p2n2
            p2n3
            [hdfs_nm:children]
            hdfs_dn
            [hdfs:children]
            hdfs_nn
            hdfs_rm
            hdfs_hm
            hdfs_dn
            hdfs_nm
        """        
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/storm/storm_install.yml
        """
        Then 检查storm配置文件符合text中的描述
        """
            
        """ 

    Scenario: synbot启动目标机虚拟机中的storm
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在storm
        Given: 目标集群{}中目标虚拟机组{}上的storm服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/storm/storm_start.yml
        """
        Then 目标虚拟机组{}spark服务状态为启动

    Scenario: synbot关闭目标机虚拟机中的storm
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在storm
        Given: 目标集群{}中目标虚拟机组{}上的spark服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/spark/spark_stop.yml
        """
        Then 目标虚拟机组{}spark服务状态为关闭

    Scenario: synbot重启目标机虚拟机中的spark
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在spark
        Given: 目标集群{}中目标虚拟机组{}上的spark服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/spark/spark_restart.yml
        """
        Then 目标虚拟机组{}spark服务状态为启动

    Scenario: synbot重启目标机虚拟机中的spark
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中目标虚拟机组{}存在spark
        Given: 目标集群{}中目标虚拟机组{}上的spark服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/spark/spark_restart.yml
        """
        Then 目标虚拟机组{}spark服务状态为启动