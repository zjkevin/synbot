#!/bin/bash
# author zhangjie
# date 2015-03-26
rm /bin/sh
ln -s /bin/bash /bin/sh
CUR_DIR=$(pwd)
cp $CUR_DIR/synbot_profile.sh /etc/profile.d/synbot_profile.sh
sed -is "s#^cur_dir#cur_dir=${PWD}#" /etc/profile.d/synbot_profile.sh
cp $CUR_DIR/sbc.py $CUR_DIR/sbc
chmod +x $CUR_DIR/sbc
apt-get install build-essential
apt-get install python-dev
apt-get install sshpass
apt-get install vim
pip install fabric --no-index --find-links $1
pip install ansible --no-index --find-links $1
