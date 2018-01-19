#!/bin/bash
# environment variable configuration for {{pub_install_app_name}}
export JDK_HOME={{pub_install_app_home}}
export JAVA_HOME={{pub_install_app_home}}
export CLASSPATH=.:{{pub_install_app_home}}/lib/tools.jar
export PATH=$JAVA_HOME/bin:$PATH
