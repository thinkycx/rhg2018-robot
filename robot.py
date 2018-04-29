#!/usr/bin/env python
# coding=utf-8

import api
import logging
import requests
import time
import multiprocessing
import os
import psutil
import local_server

download_binary_pass = 0



CHALLENGE_PATH = "challenges/"
SLEEP_MAIN_SECOND = 5
FUZZ_NUM = 4
MAX_FUZZ_TIME = 60


class Challenge(object):
    """
    对应官方下载的每一个题目
    """
    def __init__(self, challenge, bin_path):
        """ init """
        self._vm_name = challenge['vm_name']
        self._score = challenge['score']
        self._vm_ip = challenge['vm_ip']
        self._challengeID = challenge['challengeID']
        self._binaryUrl = challenge['binaryUrl']
        self._question_port = challenge['question_port']
        self.bin_path = bin_path

        self.priority_mark = 1000
        self.fuzz_status = False
        self.exploit_status = False
        self.submit_status = False

    def get_id(self):
        return self._challengeID

    def get_bin_path(self):
        return self.bin_path

    def set_priority_mark(self, priority_mark):
        self.priority_mark = priority_mark

    def get_priority_mark(self):
        return self.priority_mark

    def set_fuzz_status(self, fuzz_status):
        self.fuzz_status = fuzz_status

    def get_fuzz_status(self):
        return self.fuzz_status

    def set_exploit_status(self, exploit_status):
        self.exploit_status = exploit_status

    def get_exploit_status(self):
        return self.exploit_status

    def set_submit_status(self, submit_status):
        self.submit_status = submit_status

    def get_submit_status(self):
        return self.submit_status



class AFLRobot(object):
    """
    对于fuzz模块的封装类
    """
    def __init__(self, challengeID, bin_path): #  bin_path can be deleted later?
        self._challengeID = challengeID
        self._bin_path = bin_path

        self.running_status =  False
        self.start_time = None
        self.total_time = 0
        self.running_times = 0
        self.proc = None
        self.pid = None

    def get_id(self):
        return self._challengeID

    def get_running_status(self):
        return self.running_status

    def set_running_status(self, status):
        self.running_status = status

    def get_start_time(self):
        return self.start_time

    def set_start_time(self, time):
        self.start_time = time

    def get_total_time(self):
        return self.total_time

    def add_total_time(self,running_time):
        self.total_time += running_time

    def get_running_times(self):
        return self.running_times

    def add_running_times(self):
        self.running_times += 1

    def get_proc(self):
        return self.proc

    def set_proc(self, proc):
        self.proc = proc

    def get_pid(self):
        return self.pid

    def set_pid(self, pid):
        self.pid = pid

    def start_fuzz(self):
        """
        根据_bin_path来开始fuzz
        需要根据fuzz模块二次修改
        :return:
        """
        # 创建fuzz对象，暂时用ｓｌｅｅｐ替代
        time.sleep(100000)

    def get_crash(self):
        """
        从fuzz模块获取crash的列表
        否则，返回Ｆａｌｓｅ
        :return:
        """
        return False

    def submit_crash(self):
        """
        把crash提交给exploit模块，记录crash hash，每次提交不同的值
        :return:
        """


class EXPRobot(object):
    def __init__(self, challengeID, bin_path):
        self._challengeID = challengeID
        self._bin_path = bin_path

    def start_exploit(self):
        """
        需要传递的参数：
            bin path
            crash 列表
        :return:
        """

    def get_exploit(self):
        """
        获取攻击流量
        :return:
        """











def initial(challenge_list, aflrobot_list):
    """
    download challenges and initial challenge_list
    :param challenge_list:
    :return:
    """
    print "\t[*] initial..."
    api.make_folder(CHALLENGE_PATH)
    challenge_download_list = api.get_question_status()
    file_number = 0

    for c_d_l in challenge_download_list:
        logging.info(c_d_l)
        id = c_d_l['challengeID']
        dir_name = unicode(id) + "/"
        file_name = "bin"
        target_dir = CHALLENGE_PATH + dir_name
        binary_path = CHALLENGE_PATH + dir_name +  file_name
        api.make_folder(target_dir)
        if not download_binary_pass:
            try:
                logging.info("downloading binary %d" % id)
                r = requests.get(c_d_l['binaryUrl'], headers = {'User-Agent': 'curl / 7.47.0'}, timeout=100)
                with open(binary_path, "wb") as f:
                    f.write(r.content)
                file_number += 1
            except Exception as e:
                logging.info(unicode(e))
                exit(-1)
        else:
            print "\t[!] USE OLD BINARY"
        # initial challenge_list
        challenge = Challenge(c_d_l, binary_path)
        challenge_list.append(challenge)

        # intial aflrobot_list
        aflrobot = AFLRobot(id, binary_path)
        aflrobot_list.append(aflrobot)

    print "\t[+] download %d files success..." % file_number
    print "\t[+] initial challenge_list success..."
    print "\t[-] challenge_list %s " % challenge_list

def worker_fuzz(aflrobot):
    """
    worker_fuzz是新开启的进程将要执行的函数
    新建一个AFLRobot对象开始FUZZ
    :param aflrobot: 当前task的状态，根据task_dict_content修改而来
    :return:
    """
    pid = os.getpid()
    print "\t\t\t [+]work_fuzz %d ..." % pid
    aflrobot.set_pid(pid)
    aflrobot.start_fuzz()


def get_challenge_by_id(id, challenge_list):
    for c in challenge_list:
        if c.get_id() == id:
            return c

def get_aflrobot_by_id(id, aflrobot_list):
    for r in aflrobot_list:
        if r.get_id() == id:
            return r

def get_running_aflrobot_list(aflrobot_list):
    running_aflrobot_list = []
    for aflrobot in aflrobot_list:
        if aflrobot.get_running_status() == True:
            running_aflrobot_list.append(aflrobot)
    return running_aflrobot_list


def start_new_aflrobot(aflrobot_list, challenge_list):
    """
    开始运行新的robot
    :param aflrobot_list:
    :param challenge_list:
    :return:
    """
    print "\t [*] start_new_aflrobot..."
    running_robot_num = len(get_running_aflrobot_list(aflrobot_list))

    if running_robot_num >= FUZZ_NUM:
        print "\t\t [!] EXCEED MAXIUM FUZZ_NUM, running_robot_num # %d " % running_robot_num
    else:
        has_fuzz = 0
        while running_robot_num < FUZZ_NUM:
            # 是否还有未FUZZ的CHALLENGE
            for challenge in challenge_list:
                if challenge.get_submit_status() == False & challenge.get_fuzz_status() == False:
                    has_fuzz = 1
                    break
            if has_fuzz == 0:
                loggging.warinig("NOTHING TO BE FUZZED!")
                break

            # 取出分数最高的challenge_id
            max_id, max = -1, -10000000000
            for challenge in challenge_list:
                # 取出尚未FUZZ的challenge
                if challenge.get_submit_status() == True | challenge.get_fuzz_status() == True:
                    continue
                temp = challenge.get_priority_mark()
                if temp > max:
                    max = temp
                    max_id = challenge.get_id()
            # now_task = sorted(task_dict.items(), lambda x, y: cmp(x[1]["priority_mark"], y[1]["priority_mark"]))[0]
            # 运行aflrobot_list　中的机器人
            if max_id != -1:
                # 修改challenge信息
                print "\t\t" + "*" * 100
                challenge = get_challenge_by_id(max_id, challenge_list)
                priority_mark = challenge.get_priority_mark()
                challenge.set_priority_mark(priority_mark - 1)
                challenge.set_fuzz_status(True)
                print "\t\t [+] START NEW CHALLENGE! ID # %d ,priority_mark # %d" % (max_id, priority_mark)

                # 创建进程运行AFLRobot机器人
                aflrobot = get_aflrobot_by_id(max_id, aflrobot_list)
                aflrobot.set_running_status(True)
                aflrobot.set_start_time(time.time())
                aflrobot.add_running_times()

                proc = multiprocessing.Process(target=worker_fuzz, args=(aflrobot,))
                proc.deamon = True
                aflrobot.set_proc(proc)

                proc.start()

                running_robot_num = len(get_running_aflrobot_list(aflrobot_list))
            print "\t\t [+] now running_robot_num  is  %d " % running_robot_num



def check_aflrobot_list(aflrobot_list, challenge_list):
    """
    判断是否有AFLRobot不需要继续运行了
        运行时间超过 > MAX_FUZZ_TIME

    :param aflrobot_list:
    :param challenge_list:
    :return:
    """
    print "\t [*] check_aflrobot_list"

    running_aflrobot_list = get_running_aflrobot_list(aflrobot_list)
    for aflrobot in running_aflrobot_list:
        id = aflrobot.get_id()
        running_time =  time.time() - aflrobot.get_start_time()
        if running_time > MAX_FUZZ_TIME:
            print "\t\t DELETE challenge %d ,running_time is %d" % (id, running_time)
            # 后期加入数据恢复功能
            # stop this aflrobot

            proc = aflrobot.get_proc()
            if proc.is_alive():
                print "\t\t Terminating %s" % proc
                proc.terminate()

                aflrobot.set_running_status(False)
                aflrobot.add_total_time(running_time)

                aflrobot.set_start_time(None)
                aflrobot.set_pid(None)
                aflrobot.set_proc(None)

                challenge = get_challenge_by_id(id, challenge_list)
                challenge.set_fuzz_status(False)



def start_robot_server():
    proc = multiprocessing.Process(target=local_server.main )
    proc.deamon = True
    proc.start()

if __name__ == "__main__":
    start_robot_server()

    challenge_list = []
    aflrobot_list = []
    exploit_list = []

    print "[1] INITIAL...."
    initial(challenge_list, aflrobot_list)

    while True:
        print "\n" * 4
        print "-"*100
        print "[2] FUZZ...."
        start_new_aflrobot(aflrobot_list, challenge_list)
        check_aflrobot_list(aflrobot_list, challenge_list)


        print "[3] EXPLOIT...."
        #start_new_exprobot(exploit_list, challenge_list)
        #check_exprobot_list(exploit_list, challenge_list)


        print "[4] SUBMIT...."


        print "\t MAIN sleep %d seconds " % SLEEP_MAIN_SECOND
        time.sleep(SLEEP_MAIN_SECOND)





















