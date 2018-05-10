#!/bin/bash 
echo core >/proc/sys/kernel/core_pattern 
rm submit_log.txt
python robot.py
