# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess as sub
from nose.tools import *

_debsource_url = r'192.168.68.17'
_debsource_port = 8081
_debsource_file = r'/etc/apt/sources.list'
_pipsource_url = r'192.168.68.17'
_pipsource_port = 8082


hos1={"ip":"","disk":{}}


@given(u'CN机器上配置的debian源')
def debian_source(context):
    if os.path.exists(_debsource_file):
        os.remove(_debsource_file)
    with open(_debsource_file,'a') as files:
        for i in xrange(1,6):
            files.write("deb http://%s:%s/p%d/debian/ wheezy contrib main\n" %(_debsource_url,_debsource_port,i))
        os.system('apt-get update')

@given(u'安装synbot')
def synbot_install(context):
    os.system('sh %s/synbot_install.sh %s:%d' %(context.conf.synbot_dir,_pipsource_url,_pipsource_port))
    os.system('source /etc/profile')

@given(u'CN上生成ssh密钥和公钥')
def ssh_create(context):
    if not(os.path.exists('/root/.ssh/id_rsa')):
        os.system("ssh-keygen -t rsa -C 'my synbot key'<<EOF\n\n\nEOF")
    if os.path.exists('/root/.ssh/id_rsa') and not(os.path.exists('/root/.ssh/id_rsa.pub')):
        os.system("ssh-keygen -t rsa -C 'my synbot key'<<EOF\ny\n\nEOF")

@when(u'进入到synbot根目录执行 {sbcshell} 命令')
def execute_sbc(context,sbcshell):
    context.response = sub.check_output('cd /usr/synbot&&%s' % sbcshell,shell=True)

@then(u'sbc -cn Response的结果与预期结果相匹配')
def verify_cn(context):
    str_hv = ["the ssh config file '/root/.ssh/config' is ok","the ssh id_rsa file '/root/.ssh/id_rsa.pub' is ok","the ssh id_rsa.pub file '/root/.ssh/id_rsa.pub' is ok","the user is root","package 'Fabric' is ok","package 'Ansible' is ok","debian source address:http://192.168.68.17:8081/p1 is online","debian source address:http://192.168.68.17:8081/p2 is online","debian source address:http://192.168.68.17:8081/p3 is online","debian source address:http://192.168.68.17:8081/p4 is online","debian source address:http://192.168.68.17:8081/p5 is online","debian source address:http://192.168.68.17:8081/p6 is online","pip source address:http://192.168.68.17:8082 is online","vmtemplet.xml' is ok","debian71.img.tar.gz' is ok"]

    str_vm = ["the ssh config file '/root/.ssh/config' is ok","the ssh id_rsa file '/root/.ssh/id_rsa.pub' is ok","the ssh id_rsa.pub file '/root/.ssh/id_rsa.pub' is ok","the user is root","package 'Fabric' is ok","package 'Ansible' is ok","debian source address:http://192.168.68.17:8081/p1 is online","debian source address:http://192.168.68.17:8081/p2 is online","debian source address:http://192.168.68.17:8081/p3 is online","debian source address:http://192.168.68.17:8081/p4 is online","debian source address:http://192.168.68.17:8081/p5 is online","debian source address:http://192.168.68.17:8081/p6 is online","pip source address:http://192.168.68.17:8082 is online","vmtemplet.xml' is ok","debian71.img.tar.gz' is ok"]
    error = []

    if context.response.find("mode:vm") == -1:
        for s in str_hv:
            else
                error.append(s)
    else:

    result = []
    for i in str1:
        if context.response.find(i) == -1:
            result.append(0)
        else:
            result.append(1)
    if str2.find("mode:vm") == -1:
        assert_equals(expected_hv,result)
    else:
        assert_equals(expected_vm,result)

@then(u'验证synbot处于{mode}安装集群')
def verify_mode(context,mode):
    lst1 = []
    lst2 = []
    with open('%s/synbot.ini'%context.conf.synbot_dir,'r') as files:
        lst1 = files.read().split('base = ')
        lst2 = lst1[1].split('\n')
        assert_equals(mode,lst2[0])

@given(u'CN机器的/etc/hosts里需要存在poc1、poc2记录')
def exists_CN_hosts(context):
    with open('/etc/hosts','a+') as files:
        str = files.read()
        for i in ('192.168.68.17 poc1','192.168.68.18 poc2'):
            if str.find(i) == -1:
                files.write('\n%s'%(i))


@given(u'CN机器的/usr/synbot/hosts的[mother_land],[installvm]里分别存在poc1、poc2')
def exists_synbot_hosts(context):
    lst1 = []
    lst2 = []
    lst3 = []
    with open('/usr/synbot/hosts','w+') as files:
        str1 = files.read()
        lst1 = str1.strip().split('[updateimg]')
        if lst1[0].find('poc1') == -1:
            str1.replace('[mother_land]','[mother_land]\npoc1')
            files.write(str1)

        lst2 = str1.strip().split('[installvm]')
        lst3 = lst2[1].strip().split('[startvm]')
        if lst3[0].find('poc2') == -1:
            str1.replace('[installvm]','[installvm]\npoc2')
            files.write(str1)

@given(u'两台目标机的机器密码为synway')



@given(u'两台目标机的主机名为poc1、poc2')
def testmac_hostname(context):
    x = [('context.testmac1','poc1'),('context.testmac2','poc2')]
    for i in xrange(len(x)):
        sub.check_call('sshpass -p synway scp resource/basic_function/hostname root@%s:/etc' % x[i][0], shell= true)
        sub.check_call('sshpass -p synway ssh root@%s "echo %s > /etc/hostname"' %(x[i][0],x[i][1]), shell= true)
        sub.check_call('sshpass -p synway ssh root@%s "sudo /etc/init.d/hostname.sh start"' %(x[i][0]), shell= true)

@given(u'删除两台目标机原有的CN机器公钥')
def delete_authorized_keys(context):
    sub.check_call('sshpass -p synway ssh root@%s "rm /root/.ssh/authorized_keys"' % context.testmac1, shell= true)










if __name__ == '__main__':
    debian_source()