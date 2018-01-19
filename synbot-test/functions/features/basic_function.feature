# -*- coding: utf-8 -*-

Feature: synbot基本常用功能

    Background: CN机安装synbot
        Given CN机器上配置的debian源
        And 安装synbot

    Scenario: sbc -cn synbot安装状态信息
        When 进入到synbot根目录执行 "sbc -cn" 命令
        Then sbc -cn Response的结果与预期结果相匹配

    Scenario: sbc -hvmode 切换至基于物理机安装集群
        When 进入到synbot根目录执行 "sbc -hvmode" 命令
        Then 验证synbot处于hv安装集群


    Scenario: sbc -vmmode 切换至基于虚拟机安装集群
        When 进入到synbot根目录执行 "sbc -vmmode" 命令
        Then 验证synbot处于vm安装集群

    Scenario Outline: sbc -ssh 公钥分发
        Given CN机器的/etc/hosts里需要存在poc1、poc2记录
        And CN机器的/usr/synbot/hosts的[mother_land],[installvm]里分别存在poc1、poc2
        And CN上生成ssh密钥和公钥
        And 两台目标机的机器密码为synway
        And 两台目标机的主机名为poc1、poc2
        And 删除两台目标机原有的CN机器公钥
        When 进入到synbot根目录执行 "sbc -ssh" 命令

        

        Then 验证进入目标机不需要密码
        When 进入到synbot根目录执行 "sbc -ssh poc2" 命令
        Then 验证进入目标机不需要密码
        When 进入到synbot根目录执行 "sbc -ssh poc[1~2]" 命令
        Then 验证进入目标机不需要密码


    Scenario: sbc -ping ping机器组



    Scenario: sbc -socket 检测机器组端口