#!/bin/bash
DEBPORT=$1
if [ "$DEBPORT"x == "x" ] ;then
 DEBPORT=8080
fi
#python -m SimpleHTTPServer $DEBPORT &
cd /root/pip_packages
$(nohup python -m SimpleHTTPServer $DEBPORT >& /var/log/pipserver.log < /dev/null &)


