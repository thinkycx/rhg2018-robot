import sys
import os
# usage : python WatchDog.py pyfile

def WatchDog(file):
	while True:
		os.system('python '+file)

if __name__ == '__main__':
	print sys.argv[1]
	WatchDog(sys.argv[1])