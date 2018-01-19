#!/bin/bash

# environment variable configuration
export HADOOP_HOME={{hadoop_home}}
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
export PYTHON_CMD={{python_cmd}}