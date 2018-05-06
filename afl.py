import subprocess
import os
import stat
import time
import re

"""
author: Dlive
date  : 2018/05/01
"""


"""
Dependency:
objdump binary
strings binary
afl with qemu
"""


"""
AFL need root privilege to run
"""
class AFL(object):
    # path of the binary which is going to be fuzzed
    __binary_path = None
    # binary dirname
    __binary_dirname = None
    # afl install path
    __afl_dirname = None
    # afl binary path
    __afl_fuzz_binary_path = None
    # afl process
    __afl_fuzz_process = None
    # seed files path
    __input_path = None
    # crash path
    __output_path = None
    # afl dic path
    __dic_path = None

    __debug = False

    """
    binary: path of the binary which is going be fuzzed
    afl   : path of afl-fuzz binary
    """

    def __init__(self, binary, afl='/root/afl-2.52b/afl-fuzz', debug=False):
        self.__binary_path = binary
        self.__afl_fuzz_binary_path = afl
        self.__afl_dirname = os.path.dirname(afl)
        self.__binary_dirname = os.path.dirname(binary)
        self.__input_path = os.path.join(self.__binary_dirname, 'in')
        self.__output_path = os.path.join(self.__binary_dirname, 'out')
        self.__dic_path = os.path.join(self.__binary_dirname, 'dic')
        self.__debug = debug

        if self.__debug:
            print '__binary_path', self.__binary_path
            print '__binary_dirname', self.__binary_dirname
            print '__afl_dirname', self.__afl_dirname
            print '__afl_fuzz_binary_path', self.__afl_fuzz_binary_path
            print '__afl_fuzz_process', self.__afl_fuzz_process
            print '__input_path', self.__input_path
            print '__output_path', self.__output_path
            print '__dic_path', self.__dic_path

    def _generate_afl_dic(self):
        afl_dic_script = """#!/bin/bash

objdump -d "${1}" | grep -Eo '$0x[0-9a-f]+' | cut -c 2- | sort -u | while read const; do echo $const | python -c 'import sys,   struct; sys.stdout.write("".join(struct.pack("<I" if   len(l) <= 11 else "<Q", int(l,0)) for l in   sys.stdin.readlines()))' > ${2}/$const; done
i=0; strings "${1}"| while read line; do echo -n "$line" > ${2}/string_${i} ; i=$[ $i + 1 ] ; done
"""
        afl_dic_script_path = os.path.join(self.__afl_dirname, 'afl_dic.sh')
        if not os.path.exists(afl_dic_script_path):
            with open(afl_dic_script_path, 'w') as f:
                f.write(afl_dic_script)
        os.chmod(afl_dic_script_path, 0775)

        if not os.path.exists(self.__dic_path):
            os.mkdir(self.__dic_path)

        return subprocess.call([afl_dic_script_path, self.__binary_path, self.__dic_path])

    def start(self):
        self._generate_afl_dic()
        for f in os.listdir(self.__dic_path):
            filename = os.path.join(self.__dic_path, f)
            if os.stat(filename).st_size > 128:
                os.remove(filename)
        if not os.path.exists(self.__input_path):
            os.mkdir(self.__input_path)
            with open(os.path.join(self.__input_path, 'demo.txt'), 'w') as f:
                f.write('DEMO')
        if not os.path.exists(self.__output_path):
            os.mkdir(self.__output_path)
        else:
            self.__input_path = '-'

        os.chmod(self.__binary_path, 0775)

        if self.__debug:
            print "afl command:", self.__afl_fuzz_binary_path, '-i', self.__input_path, '-o', self.__output_path, '-x', self.__dic_path, '-m none', '-Q', '--', self.__binary_path

            self.__afl_process = subprocess.Popen([self.__afl_fuzz_binary_path,'-i', self.__input_path, '-o', self.__output_path, '-x', self.__dic_path, '-m', 'none', '-Q', '--', self.__binary_path ])
        else:
            self.__afl_process = subprocess.Popen([self.__afl_fuzz_binary_path,'-i', self.__input_path, '-o', self.__output_path, '-x', self.__dic_path, '-m', 'none', '-Q', '--', self.__binary_path ], stdout=subprocess.PIPE)

    def stop(self):
        if self.is_alive():
            self.__afl_process.kill()
            self.__afl_process.wait()

    def is_alive(self):
        return self.__afl_process.poll() is None

    def crashes(self):
        crashes_path = os.path.join(self.__output_path, 'crashes')
        if not os.path.exists(crashes_path):
            return []
        crashes = []
        for crash in os.listdir(crashes_path):
            if crash != 'README.txt':
                crashes.append(os.path.join(crashes_path, crash))
        return crashes

def check_docker():
    result = subprocess.check_output('cat /proc/1/sched | head -n 1', shell=True)
    pattern = re.compile('[0-9]+')
    pid = int(pattern.findall(result)[0])
    if pid > 1:
        return True
    else:
        return False

if __name__ == '__main__':
    if check_docker():
        afl_path = '/root/afl-2.52b/afl-fuzz'
    else:
        afl_path = '/home/thinkycx/fuzz/afl-2.52b/afl-fuzz'
    max_run_time = 600
    for i in range(10000):
        start_time = time.time()
        i = i%9+2
        file_name = './challenges/{}/bin'.format(i)
        afl = AFL(file_name, afl=afl_path, debug=True )
        afl.start()
        crashes = afl.crashes()
        print file_name
        print "crashes ", crashes

        crashes = afl.crashes()
        print file_name
        print "crashes ", crashes

        while True:
            if time.time() - start_time >max_run_time:
                break

            time.sleep(20)
            print  "is_alive", afl.is_alive()
            tmp = afl.crashes()
            if crashes != tmp:
                print "time ", time.time() - start_time
                print "crashes ", crashes
                crashes = tmp

        afl.stop()

