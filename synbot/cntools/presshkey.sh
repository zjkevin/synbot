#!/bin/bash

ssh-keygen -t rsa

if [ -f "~/.ssh/config" ]; then
 echo '' >> ~/.ssh/config
 cp ~/.ssh/config ~/.ssh/config.bk
else
 echo '' > ~/.ssh/config;
fi
 sed -i '/StrictHostKeyChecking/d' ~/.ssh/config
 sed -i '/UserKnownHostsFile/d' ~/.ssh/config
 sed -i '1i StrictHostKeyChecking no' ~/.ssh/config
 sed -i '2i UserKnownHostsFile /dev/null' ~/.ssh/config

exit

if [ -f "/root/.ssh/config" ]; then
 echo '' >> /root/.ssh/config
 cp /root/.ssh/config /root/.ssh/config.bk
else
 echo '' > /root/.ssh/config;
fi
 sed -i '/StrictHostKeyChecking/d' /root/.ssh/config
 sed -i '/UserKnownHostsFile/d' /root/.ssh/config
 sed -i '1i StrictHostKeyChecking no' /root/.ssh/config
 sed -i '2i UserKnownHostsFile /dev/null' /root/.ssh/config
