#!/bin/bash
ps -efj | grep afl | awk  '{print $2}' | xargs kill -9
