#!/bin/bash
count=1
while [ $count -le 2 ]; do 
    echo "---------------"
     ps -efj | grep afl | grep -v grep
    sleep 1
 done
