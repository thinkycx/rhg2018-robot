#!/usr/bin/python2
# -*- coding : utf-8 -*-
# strings needed

import re
import os
import sys

def IsInterActive(filename):
	ret = False

	pattern = re.compile(u'([0-9])(\.[ a-zA-z]+)')
	fp = os.popen('strings '+filename,'rb')
	content = fp.read()
	res = re.findall(pattern,content)

	# for i in res:
	# 	print i

	count = 0
	tmp = 0	
	option  = []
	tmp_option = []
	for i in range(1,len(res)):
		if ord(res[i-1][0])+1 == ord(res[i][0]):
			tmp += 1
			tmp_option.append(int(res[i-1][0]))
			if count < tmp:
				count = tmp
				option = tmp_option[:]
		else:
			tmp = 0
			tmp_option = []

	if count > 2:
		option.append(option[count-1]+1)
		ret = True
	else:
		ret = False
		option = []

	return ret,option

def test():
	for i in range(2,11):
		print '----------------------%d-----------------'%i
		print IsInterActive('bin'+str(i))

if __name__ == '__main__':
	test()