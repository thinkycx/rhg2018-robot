#!/usr/bin/python2
# -*- coding : utf-8 -*-
# strings needed

import re
import os
import sys
import threading
import pwn_2,pwn_3,pwn_4,pwn_5,pwn_6,pwn_7,pwn_8,pwn_9,pwn_10

class PreProcessor(object):

	def __init__(self,binary,ip,port,path,timeout=5):
		self.binary = binary
		self._isInterActive = False
		self.option = []
		self.flag = ''
		self.ip = ip
		self.port = port
		self.msg = 'cat '+path
		self.timeout = 5
		os.system('echo flag{123}>%s'%path)
		self.IsInterActive()
		self.ApplyExp()

	def IsInterActive(self):
		ret = False

		pattern = re.compile(u'([0-9])(\.[ a-zA-z]+)')
		fp = os.popen('strings '+self.binary,'rb')
		content = fp.read()
		res = re.findall(pattern,content)

		for i in res:
			print i

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

		self._isInterActive = ret
		self.option = option

	def worker(self,i):
		exec('flag = pwn_%d.exp(1,"%s","%s")'%(i,self.binary,self.msg))
		if 'flag' in flag:
			try:
				exec('flag = pwn_%d.exp(0,"%s","%s","%s",%d,%d)'%(i,self.binary,self.msg,self.ip,self.port,self.timeout))
				# print flag
				if 'flag' in flag:
					self.flag = flag
			except:
				pass

	def ApplyExp(self):
		thread_list = []
		for i in range(2,11):
			t = threading.Thread(target=self.worker,args=(i,))
			thread_list.append(t)

		for t in thread_list:
			t.setDaemon(True)
			t.start()

		for t in thread_list:
			t.join()

	def retIsInterActive(self):
		return self._isInterActive,self.option

	def retFlag(self):
		return self.flag

def test():
	for i in range(2,11):
		print '-----------------------problem %d----------------' %i
		binary = '/home/echo/ctf/rhg/string/bin%d'%i
		ip = '127.0.0.1'
		port = 1210
		path = '/home/echo/flag'
		timeout = 5
		Processor = PreProcessor(binary,ip,port,path,timeout)
		_isInterActive,option = Processor.retIsInterActive()
		flag = Processor.retFlag()
		print flag

if __name__ == '__main__':
	test()