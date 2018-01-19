#!/bin/bash
source /etc/profile && source ~/.profile

#显示帮助
usage()
{
	echo "用法：'$0' <sub_dir> <runtimes>"
	exit 0
}

if [ $# -lt 2 ]; then
	usage
fi

SUBDIR=$1
LOGFILE="x_rw_"$SUBDIR".log"

echo "==============TEST BEGIN===================="
echo "==============TEST BEGIN====================" >> $LOGFILE
echo "cmd:sub_dir="$1",runtimes="$2 >> $LOGFILE
date >> $LOGFILE

RROOT="/testdfs_put_"$SUBDIR
LTMP=$SUBDIR"_tmp"

totalsize_ex=0
totaltime_write_ex=0
totaltime_read_ex=0

for (( i = 0; i < $2; i++ )); do

	totaltime=0
	totaltime_read=0
	totalsize=0

	hdfs dfs -mkdir $RROOT
	mkdir $LTMP

	for file in $SUBDIR/* ; do
		#计算文件长度
		filesize=`ls -l $file | awk '{print $5}'`
		let totalsize=totalsize+filesize
	done

	let totalsize_ex=totalsize_ex+totalsize

	echo $SUBDIR",总大小:"$totalsize

	#开始并执行操作(写入)
	starttime=$SECONDS
	hdfs dfs -put -f $SUBDIR/* $RROOT

	#计算并显示执行时间
	exetime=$(expr $SECONDS - $starttime)
	echo "PUT耗时(秒)："$exetime

	#计算总时间
	let totaltime=totaltime+exetime
	let exetime_write=exetime
	echo "PUTDIR|"$SUBDIR"_",SIZE":"$totalsize",EXETIME(S):"$exetime # >> $LOGFILE

	starttime=$SECONDS
	hdfs dfs -get -crc $RROOT/* $LTMP
	#计算并显示执行时间
	exetime=$(expr $SECONDS - $starttime)
	echo "GET耗时(秒)："$exetime

	#计算总时间
	let totaltime_read=totaltime_read+exetime
	let exetime_read=exetime
	echo "GETDIR|"$RROOT"_",SIZE":"$totalsize",EXETIME(S):"$exetime # $LOGFILE

	echo "DIR,TOTALSIZE,PUTDIR,GETDIR" >> $LOGFILE
	echo $SUBDIR","$totalsize","$exetime_write","$exetime_read >> $LOGFILE

	let totaltime_read_ex=totaltime_read_ex+exetime_read
	let totaltime_write_ex=totaltime_write_ex+exetime_write

	hdfs dfs -rm -r $RROOT
	rm -r $LTMP

done

AVG_PUT=$(expr $totalsize_ex / $totaltime_write_ex)
AVG_GET=$(expr $totalsize_ex / $totaltime_read_ex)
echo "TOTALSIZE,PUT(B/S),GET(B/S)" >> $LOGFILE
echo $totalsize","$AVG_PUT","$AVG_GET >> $LOGFILE
