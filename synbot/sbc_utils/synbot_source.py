#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os,sys
import re
import paramiko
from fabric.colors import *
from synbot_paramiko import *
sys.path.append('..')
import synbot_env

DEB_FLAG_FILE = '/var/www/port_flag/deb_port_flag'
PIP_FLAG_FILE = '/var/www/port_flag/pip_port_flag'
sbcenv = synbot_env.get_synbot_ini()
USER_NAME = sbcenv.cluster_username
PASSWORD = sbcenv.cluster_passwd
DEB_SH_PATH = '/var/www/debianiso'
PIP_SH_PATH = '/var/www/pip_packages'
SH_FILE = '../cntools/debserver.sh'

#获取cntools/debserver.sh文件，并通过传参修改文件中的路径和端口
def temp_file(path,port):
    new_dir = "cd %s\n" % path
    new_port = 'DEBPORT = %s\n' % port
    lines=open(SH_FILE).readlines()
    for i in xrange(0,len(lines)):
        if lines[i].startswith('cd '):
            lines[i]= new_dir
        if lines[i].strip().startswith('DEBPORT=')  or lines[i].strip().startswith('DEBPORT ='):
            items = lines[i].split('=')[1].strip()
            m = re.match(r'^\d+',items)
            if m:
                lines[i] = new_port
    f=open(SH_FILE,'w')
    f.writelines(lines)
    f.close()

# deploy debian source
def deploy_debian(debian_source_iso,debian_source_host,debian_source_port,mount_point,log_dir):
    ssh = paramiko_init(debian_source_host,USER_NAME,PASSWORD)
    temp_file(debian_source_iso,debian_source_port)
    stdin,stdout,stderr = ssh.exec_command(" scp %s root@%s:%s " %(SH_FILE,debian_source_host,DEB_SH_PATH))
    #判断传参指定的目录下是否存在源文件
    # stdin,stdout,stderr = ssh.exec_command(" cd %s && ls *.iso > %s/iso_tmp.txt && grep -c  '.iso' iso_tmp.txt" %(debian_source_iso,debian_source_iso))
    stdin,stdout,stderr = ssh.exec_command(" cd %s && ls *.iso | grep -c '.iso'" % debian_source_iso)
    err = stderr.read()
    out = int(stdout.read())
    #如果不存在
    if err != '':
        print red(" The %s or debian ISO files not exits! Please set them first! " % debian_source_iso)
        exit(1)
    #如果存在debian镜像文件
    else:
        for i in xrange(1,out+1):
            stdin,stdout,stderr = ssh.exec_command(" ls %s|sed -n '%sp' " % (debian_source_iso,i))
            iso_dir = stdout.read()
            # source_dir = source_dir.split('.iso')[0]
            source_dir = debian_source_iso+'/'+iso_dir 
            m_point = '%s/p%s' %(mount_point,i)
            #创建挂载点目录
            stdin,stdout,stderr = ssh.exec_command("ls %s" % m_point)
            if stderr.read() != '':
                stdin,stdout,stderr = ssh.exec_command(" mkdir -p %s " % m_point)
            stdin,stdout,stderr = ssh.exec_command("grep -wq %s /etc/fstab ; echo $? " % m_point)
            if int(stdout.read()) == 0:
                stdin,stdout,stderr = ssh.exec_command("umount %s ; sed -i 's&%s&EXOX&;/EXOX/d' /etc/fstab" % (m_point,m_point))
                stdin,stdout,stderr = ssh.exec_command(" echo %s  %s  iso9660  user,auto,ro  0  0 >> /etc/fstab\n " % (source_dir.strip('\n'),m_point))
            else:
                stdin,stdout,stderr = ssh.exec_command(" echo %s  %s  iso9660  user,auto,ro  0  0 >> /etc/fstab\n " % (source_dir.strip('\n'),m_point))
            stdin,stdout,stderr = ssh.exec_command(" mount -a ")
        #创建要写入debian源部署时使用端口的文件
        stdin,stdout,stderr = ssh.exec_command("ls %s" % DEB_FLAG_FILE)
        if stderr.read() != '':
            stdin,stdout,stderr = ssh.exec_command("touch %s" % DEB_FLAG_FILE)
        #判断当前传入的端口是否被占用
        stdin,stdout,stderr = ssh.exec_command("netstat -anp|grep %s" % debian_source_port)
        if stdout.read() != '':
            #判断对应的文件中是否有该端口号
            stdin,stdout,stderr = ssh.exec_command("grep -wq %s %s;echo $?" %(debian_source_port,DEB_FLAG_FILE))
            if int(stdout.read()) != 0:
                print red("The port %s is for debian_source used! Please choose another port!!!" % debian_source_port)
                exit(1)
            else:
                stdin,stdout,stderr = ssh.exec_command(" sed -i '/%s/d' %s;echo %s >> %s" %(debian_source_port,DEB_FLAG_FILE,debian_source_port,DEB_FLAG_FILE))
        else:
            stdin,stdout,stderr = ssh.exec_command(" sed -i '/%s/d' %s;echo %s >> %s" %(debian_source_port,DEB_FLAG_FILE,debian_source_port,DEB_FLAG_FILE))
            stdin,stdout,stderr = ssh.exec_command("cd %s ; nohup python -m SimpleHTTPServer %s >& %s < /dev/null &" %(mount_point,debian_source_port,log_dir))

        ssh.close()

# deploy pip source
def deploy_pip(pip_source_dir,pip_source_host,pip_source_port,log_dir):
    ssh = paramiko_init(pip_source_host,USER_NAME,PASSWORD)
    temp_file(pip_source_iso,pip_source_port)
    stdin,stdout,stderr = ssh.exec_command(" scp %s root@%s:%s " %(SH_FILE,debian_source_host,DEB_SH_PATH))
    stdin,stdout,stderr = ssh.exec_command("ls %s" % PIP_FLAG_FILE)
    if stderr.read() != '':
        stdin,stdout,stderr = ssh.exec_command("touch %s" % PIP_FLAG_FILE)
    stdin,stdout,stderr = ssh.exec_command("netstat -anp|grep %s" % pip_source_port)
    if stdout.read() != '':
        stdin,stdout,stderr = ssh.exec_command("grep -wq %s %s;echo $?" %(pip_source_port,PIP_FLAG_FILE))
        if int(stdout.read()) != 0:
            print red("The port %s for pip_source is used! Please choose another port!!!" % pip_source_port)
            exit(1)
        else:
            stdin,stdout,stderr = ssh.exec_command(" sed -i '/%s/d' %s;echo %s >> %s" %(pip_source_port,PIP_FLAG_FILE,pip_source_port,PIP_FLAG_FILE))
    else:
        stdin,stdout,stderr = ssh.exec_command(" sed -i '/%s/d' %s;echo %s > %s" %(pip_source_port,PIP_FLAG_FILE,pip_source_port,PIP_FLAG_FILE))
        stdin,stdout,stderr = ssh.exec_command("cd %s ; nohup python -m SimpleHTTPServer %s >& %s < /dev/null &" %(pip_source_dir,pip_source_port,log_dir))
    ssh.close()


# if __name__ == '__main__':
#     deploy_debian('/root/debsource','/var/www/deb71amd64','/var/log/deb_source_server.log','8082')
#     deploy_pip('/var/www/pip_packages','/var/log/pip_source_server.log')
