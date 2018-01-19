#!/bin/bash
source /etc/profile && source ~/.profile

usage()
{
	echo "用法：'$0' <并发数>"
	exit 0
}

if [ $# -lt 1 ]; then
	usage
fi

MAXFILES=$1

[ -n $MAXFILES ] || MAXFILES=10


for (( i = 1; i <= $MAXFILES; i++ )); do
{
	./testdfs-rw.sh "bb"$i 1 5
}&
done;

for (( i = 1; i <= $MAXFILES; i++ )); do
{
	./testdfs-rw.sh "b"$i 1 5
}&
done;

wait