#!/bin/bash
# environment variable configuration for zookeepr
export HIVE_HOME={{hive_home}}
export PATH=$HIVE_HOME/bin:$PATH
export CLASSPATH=$HIVE_HOME/lib:$CLASSPATH
