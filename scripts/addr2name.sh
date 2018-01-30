#!/bin/bash 
file=$1
for addr in `ps | awk -F ',' 'BEGIN {count=0;} {count++;if(count>=4675 && count <= 4875){print $4;}}' $file | sed 's/^0*//'`
do 
   nm ~/research/kernelDebug/linux-3.5.4/vmlinux | grep $addr >> a.txt
done
