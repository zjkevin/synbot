#!/bin/bash

#test client
REMOTE_CLIENT="p5n7"
#remote workdir
WORK_DIR="~/dfs_test2"

#clusters named as hdfsN
for (( clusterIndex = 1; clusterIndex <= 4; clusterIndex++ )); do
	for (( rep = 2; rep <= 5; rep++ )); do
	   CLUSTER=hdfs${clusterIndex}
	   #reformat (init) hdfs cluster
	   ansible-playbook dfs_reformat.yml -e{dfsc=${CLUSTER},flag_clean_dfs_data=true,dfs_replication=${rep}} -v
	   #dump cluster config to the test clients
	   ansible-playbook dfs_dump_cfg.yml -e{dfsc=${CLUSTER},pub_vars_dump_path=${WORK_DIR},dfs_replication=${rep}} -v
	   #run test on hdfs cluster
	   fab dfs.testdfsc:hosts=${REMOTE_CLIENT},huser=hadoop,pwd=hadoop,cluster=${CLUSTER},workdir=${WORK_DIR}
	   ansible-playbook dfs_stop.yml -edfsc=${CLUSTER} -v
	done
done

##0808
#dfsc:hdfs1
#rep=3,11

##0809
#dfsc:2