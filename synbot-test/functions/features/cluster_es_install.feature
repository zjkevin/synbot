# -*- coding: utf-8 -*-

Feature: elasticsearch的安装和启停

    Scenario: synbot向目标机虚拟机中安装elasticsearch
        Given: 存在测试集群, SSH已经可以远程控制
        When 向synbot提交text中描述的命令
        """
            ansible-playbook books/es/es_install.yml -e esc=es -e esc_name=esc_feature
        """
        Then 检查es配置文件符合text中的描述
        """
            
        """