#!/bin/bash

#test client
REMOTE_CLIENT="p5n7"
#remote workdir
WORK_DIR="~/dfs_test2"

sleep 8h

#clusters named as hdfsN
for (( clusterIndex = 1; clusterIndex <= 1; clusterIndex++ )); do
	BUFSIZE=0
	for (( index = 1; index <= 4; index++ )); do
	   CLUSTER=hdfs${clusterIndex}
	   DFS_REP=3
	   let BUFSIZE=index*512*1024
	   #reformat (init) hdfs cluster
	   ansible-playbook dfs_reformat.yml -e{dfsc=${CLUSTER},flag_clean_dfs_data=true,dfs_replication=${DFS_REP},io_file_buffer_size=${BUFSIZE}} -v
	   #dump cluster config to the test clients
	   ansible-playbook dfs_dump_cfg.yml -e{dfsc=${CLUSTER},pub_vars_dump_path=${WORK_DIR},dfs_replication=${DFS_REP},io_file_buffer_size=${BUFSIZE}} -v

	   #run test on hdfs cluster
	   fab dfs.testdfsc:hosts=${REMOTE_CLIENT},huser=hadoop,pwd=hadoop,cluster=${CLUSTER},workdir=${WORK_DIR}
	   ansible-playbook dfs_stop.yml -edfsc=${CLUSTER} -v
	done
done

#clusters named as hdfsN
for (( clusterIndex = 1; clusterIndex <= 1; clusterIndex++ )); do
	BUFSIZE=0
	for (( index = 1; index <= 4; index++ )); do
	   CLUSTER=hdfs${clusterIndex}
	   DFS_REP=3
	   let BUFSIZE=index*512*1024
	   #reformat (init) hdfs cluster
	   ansible-playbook dfs_reformat.yml -e{dfsc=${CLUSTER},flag_clean_dfs_data=true,dfs_replication=${DFS_REP},io_file_buffer_size=2097152,dfs_stream_buffer_size=${BUFSIZE}} -v
	   #dump cluster config to the test clients
	   ansible-playbook dfs_dump_cfg.yml -e{dfsc=${CLUSTER},pub_vars_dump_path=${WORK_DIR},dfs_replication=${DFS_REP},io_file_buffer_size=2097152,dfs_stream_buffer_size=${BUFSIZE}} -v

	   #run test on hdfs cluster
	   fab dfs.testdfsc:hosts=${REMOTE_CLIENT},huser=hadoop,pwd=hadoop,cluster=${CLUSTER},workdir=${WORK_DIR}
	   ansible-playbook dfs_stop.yml -edfsc=${CLUSTER} -v
	done
done

#clusters named as hdfsN
for (( clusterIndex = 1; clusterIndex <= 1; clusterIndex++ )); do
	BUFSIZE=0
	for (( index = 1; index <= 8; index++ )); do
	   CLUSTER=hdfs${clusterIndex}
	   DFS_REP=3
	   let BLOCK_SIZE=index*1024*1024*16
	   #reformat (init) hdfs cluster
	   ansible-playbook dfs_reformat.yml -e{dfsc=${CLUSTER},flag_clean_dfs_data=true,dfs_replication=${DFS_REP},io_file_buffer_size=2097152,dfs_stream_buffer_size=2097152,dfs_blocksize=${BLOCK_SIZE}} -v
	   #dump cluster config to the test clients
	   ansible-playbook dfs_dump_cfg.yml -e{dfsc=${CLUSTER},pub_vars_dump_path=${WORK_DIR},dfs_replication=${DFS_REP},io_file_buffer_size=2097152,dfs_stream_buffer_size=2097152,dfs_blocksize=${BLOCK_SIZE}} -v

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