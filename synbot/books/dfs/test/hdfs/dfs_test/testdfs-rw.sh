#!/bin/bash
source /etc/profile && source ~/.profile

#显示帮助
usage()
{
	echo "用法：'$0' <sub_dir> <runtimes> [maxFiles]"
	exit 0
}

if [ $# -lt 2 ]; then
	usage
fi

SUBDIR=$1
LOGFILE="x_"$SUBDIR".log"

echo "==============TEST BEGIN===================="
echo "==============TEST BEGIN====================" >> $LOGFILE
echo "cmd:sub_dir="$1",runtimes="$2 >> $LOGFILE
date >> $LOGFILE

RROOT="/testdfs_put_"$SUBDIR
LTMP=$SUBDIR"_tmp"

hdfs dfs -mkdir $RROOT
mkdir $LTMP

totaltime=0
totaltime_read=0
totalsize=0

total_counts=0

MAXFILES=$3

[ -n $MAXFILES ] || MAXFILES=10000

for (( i = 0; i < $2; i++ )); do

	for file in $SUBDIR/* ; do

		let total_counts=total_counts+1

		[ $total_counts -le $MAXFILES ] || break

		RFILE=$RROOT"/"${file##*/}"_"$i

		#计算文件长度
		filesize=`ls -l $file | awk '{print $5}'`
		echo "第"$total_counts"个文件,"$RFILE",大小:"$filesize

		#开始并执行操作(写入)
		starttime=$SECONDS
		hdfs dfs -put -f "$file" "$RFILE"

		#计算并显示执行时间
		exetime=$(expr $SECONDS - $starttime)
		echo "PUT耗时(秒)："$exetime

		#计算总时间
		let totaltime=totaltime+exetime
		let totalsize=totalsize+filesize
		echo "PUT|"${file##*/}"_"$i,SIZE":"$filesize",EXETIME(S):"$exetime >> $LOGFILE

		#开始并执行操作(读取)
		LTMPFILE=$LTMP"/"${file##*/}"_"$i

		starttime=$SECONDS
		hdfs dfs -get -crc "$RFILE" "$LTMPFILE"
		#计算并显示执行时间
		exetime=$(expr $SECONDS - $starttime)
		echo "GET耗时(秒)："$exetime

		#计算总时间
		let totaltime_read=totaltime_read+exetime
		#let totalsize=totalsize+filesize
		echo "GET|"${file##*/}"_"$i,SIZE":"$filesize",EXETIME(S):"$exetime >> $LOGFILE

		rm "$LTMPFILE"
		rm $LTMP"/."${file##*/}"_"$i".crc"

	done
done

rm -r $LTMP

AVG_PUT=$(expr $totalsize / $totaltime)
AVG_GET=$(expr $totalsize / $totaltime_read)
echo "TOTAL,SIZE:"$totalsize",PUT_TIME(S):"$totaltime"|AVG="$AVG_PUT >> $LOGFILE
echo "TOTAL,SIZE:"$totalsize",GET_TIME(S):"$totaltime_read"|AVG="$AVG_GET >> $LOGFILE
echo "AVGPUT,AVGGET:" >> $LOGFILE
echo $AVG_PUT","$AVG_GET >> $LOGFILE

echo "TOTAL,SIZE:"$totalsize",PUT_TIME(S):"$totaltime"|AVG="$AVG_PUT
echo "TOTAL,SIZE:"$totalsize",GET_TIME(S):"$totaltime_read"|AVG="$AVG_GET

#echo "DEL "$RFILE >> $LOGFILE
hdfs dfs -rm -r -skipTrash $RROOT

date >> $LOGFILE
echo "==============TEST END===================="
echo "==============TEST END====================" >> $LOGFILE

exit




