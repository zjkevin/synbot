#!/bin/bash
#wait for a java process to started
pname=$1
timeout=$2
for (( i = 0; i < $timeout; i++ )); do
	test=`jps -l | grep $pname | awk '{print $2}'`
	if [ "" != ""$test ]; then
		break
	fi
	sleep 1
done

#12782 org.apache.zookeeper.server.quorum.QuorumPeerMain
#13506 backtype.storm.daemon.nimbus
#13967 sun.tools.jps.Jps
#16241 org.apache.hadoop.hdfs.server.namenode.NameNode
#13529 backtype.storm.ui.core