#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from pwn import *
import config
import os
import time


USER = config.USER
PWD  = config.PWD
LOCAL_API = config.LOCAL_API

URL = config.URL
GET_QUESTION_STATUS = URL + "/api/get_question_status"
GET_MACHINES_INFO = URL + "/api/get_machines_info"
RESET_QUESTION = URL + "/api/reset_question"
SUB_ANSWER = URL + "/api/sub_answer"



headers = {'User-Agent': 'curl / 7.47.0'}

#,
#        'Authorization': 'Basic dXNlcjAyOjhzdXlxQw==',
#
def get_question_status():
    try:
        print "\t [*] download from ", GET_QUESTION_STATUS
        while True:
            if LOCAL_API:
                r = requests.get(url=GET_QUESTION_STATUS, auth=(USER, PWD), headers=headers, timeout=10)
                print r.json()
                if r.json()['status'] == 0:
                    log.warn( unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  +  "waiting to start")
                    time.sleep(4)
                elif r.json()['status'] == 1:
                    log.info( unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) +  "start")
                    return r.json()['AiChallenge']

            else:
                r = requests.get(url=GET_QUESTION_STATUS, auth=(USER, PWD), headers=headers, timeout=10)
                return r.json()['AiChallenge']

    except Exception as e:
       log.warn(unicode(e))
       return False



def get_machines_info():
    try:
        r = requests.get(url=GET_MACHINES_INFO, auth=(USER, PWD), headers=headers)
        print r.json()
        return r.json()
    except Exception as e:
        return False


def sub_answer(flag):
    try:
        data = {"answer":flag} # Content-Type: application/x-www-form-urlencoded
        print data
        r = requests.post(url=SUB_ANSWER, auth=(USER,PWD), data=data, headers=headers)
        print r.json()
        status =  r.json()['status']
        # 成功：{"status":1,"msg":"success","questionScore":128,"questionRank":1}//questionScore:得分,questionRank:本次提交题目排名
        # 失败：{"status":0,"msg":"提示信息"}
        if status == 0 :
            return False
        elif status == 1:
            return True
    except Exception as e:
        print e
        return False



def reset_question():
    try:
        data = {

        }
        r = requests.post(url=RESET_QUESTION, auth=(USER, PWD), headers=headers)
        return r.json()
    except Exception as e:
        return False

def make_folder(target_path):
    try:
        if not os.path.exists(target_path):
            os.mkdir(target_path)
    except Exception as e:
        log.warn(unicode(e))
        exit(-1)


if __name__ == "__main__":
    sub_answer("flag{f5218bf1-3d7f-11e8-98ae-5254003be4ba}")



