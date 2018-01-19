#!/bin/bash

# environment variable configuration
export JAVA_HOME={{java_jdk_home}}
export JDK_HOME={{java_jdk_home}}
export CLASSPATH=.:{{java_jdk_home}}/lib/tools.jar
export PATH=$JAVA_HOME/bin:$PATH
