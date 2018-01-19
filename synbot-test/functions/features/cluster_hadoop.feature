# -*- coding: utf-8 -*-

Feature: elasticsearch的安装和启停

    Scenario: synbot向目标机虚拟机中安装hadoop
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
            ansible-playbook books/dfs/dfs_install.yml
        """
        Then 检查hadoop配置文件符合text中的描述
        """
            
        """ 

    Scenario: synbot格式化目标机集群中的hadoop集群
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hadoop集群
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
            ansible-playbook books/dfs/dfs_format.yml
        """
        Then 检查hadoop配置文件符合text中的描述
        """
            
        """        

    Scenario: synbot启动目标机虚拟机中的hadoop
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hadoop集群
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
        Given: 目标集群中hadoop集群服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/dfs/dfs_start.yml
        """
        Then 目标集群中hadoop集群服务状态为启动


    Scenario: synbot关闭目标机虚拟机中的hadoop
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hadoop集群
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
        Given: 目标集群中hadoop集群服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/dfs/dfs_stop.yml
        """
        Then 目标集群中hadoop集群服务状态为关闭

    Scenario: synbot重启目标机虚拟机中的hadoop
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hadoop集群
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
        Given: 目标集群中hadoop集群服务状态为启动
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/dfs/dfs_restart.yml
        """
        Then 目标集群中hadoop集群服务状态为启动

    Scenario: synbot重启目标机虚拟机中的hadoop
        Given: 目标集群{}中存在目标虚拟机组{} SSH已经可以远程控制
        Given: 目标集群{}中如下text描述的hadoop集群
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
        Given: 目标集群中hadoop集群服务状态为关闭
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/dfs/dfs_restart.yml
        """
        Then 目标集群中hadoop集群服务状态为启动