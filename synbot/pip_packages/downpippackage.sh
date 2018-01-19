# !/bin/bash

PIP_REQUIRE="pip_requires"
CACHE_PATH="/home/kevin/pip_dir"

while read LINE
do
#if[[ $LINE = ~^[a-zA-Z] ]];
#then
 echo $LINE;
 pip install $LINE --no-install -d $CACHE_PATH;
#fi
done < $PIP_REQUIRE
