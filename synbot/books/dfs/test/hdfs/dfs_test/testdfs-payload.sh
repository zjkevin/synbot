#!/bin/bash
source /etc/profile && source ~/.profile

#显示帮助
usage()
{
	echo "用法：'$0' <sub_dir> <runtimes>"
	exit 0
}

writedf()
{
	#write log to log file
	HOSTS=$1
	for host in `echo "${HOSTS}" | sed "s/,/\n/g"`; do
		DFRESULT=`fab -f dfs.py dfc:hosts=${host},huser=hadoop,pwd=hadoop | awk '/[0-9]+%/{print $1,$6,$7}' `
		echo $DFRESULT >> $2
	done
}

if [ $# -lt 2 ]; then
	usage
fi

SUBDIR=$1
LOGFILE="x_payload_"$SUBDIR".log"
LOGFILE_GF="x_payload_"$SUBDIR"_gf.log"
NODE_COUNT=`cat $HADOOP_HOME/etc/hadoop/slaves | awk '/^[a-z]/{print NR}' | awk 'END{print NR}'`
NODE_LIST=`cat $HADOOP_HOME/etc/hadoop/slaves | awk '/^[a-z]/{print $1}' | awk 'BEGIN {nodes=""} { if (NR>1) {nodes=$1","nodes;} else {nodes=$1;} } END{ print nodes}'`

echo "==============TEST BEGIN===================="
echo "cmd:sub_dir="$1",runtimes="$2

echo "==============TEST BEGIN====================" >> $LOGFILE
echo "cmd:sub_dir="$1",runtimes="$2 >> $LOGFILE
date >> $LOGFILE

echo "==============TEST BEGIN====================" >> $LOGFILE_GF
echo "cmd:sub_dir="$1",runtimes="$2 >> $LOGFILE_GF
echo "==============TEST BEGIN====================" >> $LOGFILE_GF
date >> $LOGFILE_GF
echo "HOST Avil(K) USE%" >> $LOGFILE_GF

RROOT="/testdfs_put_"$SUBDIR

hdfs dfs -mkdir $RROOT

writedf "${NODE_LIST}" "${LOGFILE_GF}"

echo "================">> $LOGFILE

writedf "${NODE_LIST}" "${LOGFILE_GF}"

echo "================">> $LOGFILE_GF

totalsize=0
for file in $SUBDIR/* ; do
	#计算文件长度
	filesize=`ls -l $file | awk '{print $5}'`
	let totalsize=totalsize+filesize
done
echo $SUBDIR",总大小:"$totalsize


for (( i = 1; i <= $2; i++ )); do

	totaltime=0
	totaltime_read=0

	RDIR="${RROOT}/${SUBDIR}_${i}"

	#开始并执行操作(写入)
	starttime=$SECONDS
	hdfs dfs -mkdir $RDIR
	hdfs dfs -put -f $SUBDIR/* $RDIR
	[ $? = "0" ] || break

	#计算并显示执行时间
	exetime=$(expr $SECONDS - $starttime)
	echo "PUT耗时(秒)："$exetime

	#计算总时间
	let totaltime=totaltime+exetime

	echo "${i}:PUTDIR|"$SUBDIR"_",SIZE":"$totalsize",EXETIME(S):"$exetime >> $LOGFILE
	echo "${i}:PUTDIR|"$SUBDIR"_",SIZE":"$totalsize",EXETIME(S):"$exetime >> $LOGFILE_GF

	writedf "${NODE_LIST}" "${LOGFILE_GF}"

	echo "================">> $LOGFILE_GF

done

echo "================">> $LOGFILE
writedf "${NODE_LIST}" "${LOGFILE_GF}"

echo "================">> $LOGFILE_GF
writedf "${NODE_LIST}" "${LOGFILE_GF}"

echo "==============TEST END===================="
date >> $LOGFILE
date >> $LOGFILE_GF
echo "==============TEST END====================" >> $LOGFILE
echo "==============TEST END====================" >> $LOGFILE_GF

hdfs dfs -rm -r -skipTrash $RROOT
