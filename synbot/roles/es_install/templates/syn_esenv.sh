#!/bin/bash
# environment variable configuration for zookeepr
export ES_HOME={{es_home}}
export ES_DATA_HOME={{es_data_mount|join(",")}}
export PATH=$ES_HOME/bin:$PATH
export ES_JAVA_OPTS="-Des.max-open-files=true"
export ES_HEAP_SIZE={{es_heap_size}}