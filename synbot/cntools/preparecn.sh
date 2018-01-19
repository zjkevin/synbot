#!/bin/bash
#python2.7-dev	安装fabric之前必须有这个包
aptitude -y install python2.7-dev

#sshpass	sshkey分发
aptitude -y install sshpass

#python-apt	python操作apt-pkg和apt-inst的库	
aptitude -y install python-apt

#setuptools	使用其中的 easy_install 下载，编译，安装和管理python包	
aptitude -y install python-setuptools

#pip	下载，编译，安装和管理python包	
aptitude -y install python-pip

#fabric	synbot组件	
pip install ansible

#ansible	synbot组件	
pip install fabric


