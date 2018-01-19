#!/bin/bash
source /etc/profile && source ~/.profile

CMD=./testdfs-rw.sh
CMD2=./testdfs-rw-dir.sh

$CMD big_16m_128m_25_1.35G 1 10
$CMD bigbig_128M_2G_7_5.78G 1 5
$CMD middle_1m_15m_200_645M 1 70
$CMD2 smalll_0_1m_2000_70M 5
$CMD smalll_0_1m_2000_70M_singleonly 1 40
