#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask,request  # sudo pip install Flask
import json
import os
import copy

app = Flask(__name__)

# 本地题目的下载地址
@app.route('/resources/fileupload/<int:folder_name>/bin')
def server_download(folder_name):
    """
    下载local_server文件夹中所有folder_name文件夹中的bin文件
    :param folder_name:
    :return:
    """
    folders = os.listdir("./local_server/")
    if unicode(folder_name) in folders:
        file_path = "./local_server/%s/bin" % unicode(folder_name)
        if os.path.exists(file_path):
            with open(file_path,'rb') as f:
                return f.read()
        else:
            return "file  %s not exists " % file_path
    else:
        return "folder %s not exists" % unicode(folder_name)



def make_flags():
    """
    根据local_server在/home/t/下创建flag文件，注意给ｔ文件夹权限
    :return:
    """
    flag_foder_path = "/home/t/"
    if os.path.exists(flag_foder_path):
        for folder in os.listdir("./local_server/"):
            flag_content = "flag{This is flag for challenge_id %s}" % unicode(folder)
            flag_path = flag_foder_path + "/flag%s.txt" % unicode(folder)
            with open(flag_path,'w+')  as f :
                f.write(flag_content)
            print "make_flags in %s" % flag_path
    else:
        print flag_foder_path + "not exists"
        exit(-1)


# curl -X GET  --user $user:$pwd $URL/api/get_question_status
@app.route('/api/get_question_status')
def api_get_question_status():
    """
    根据local_server文件夹下的所有文件夹生成question_status信息，并返回
    支持自定义　challengeID　vm_ip　vm_name　question_port　binaryUrl flag_path
    :return:
    """
    make_flags()
    t = {
    "AiChallenge": [  #ai比赛当前开放题目

    ],
    "AwdChallenge": [  #awd比赛当前开放题目
        {
            "vm_ip": "127.0.0.1",  #虚拟机ip
            "vm_name": "name",  #虚拟机名称
            "question_port": 8080,  #题目开放端口
            "username": "user",  #用户名
            "password": "123456",  #密码
        }
    ],
    "IwsChallenge": {
        "question_url": "http://ai.defcon.ichunqiu.com"  #靶场比赛题目url地址
    },
    "PointsInfo": [  #总得分情况
        {
            "points": 60,  #总分
            "aiPoints": 100,  #ai比赛得分
            "iswPoints": 40,   #靶场比赛得分
            "awdPoints": 40   #awd比赛得分
        }
    ]}
    challenge_dict_raw =         {
            "challengeID": 1,  #题目编号
            "score": 1,  #得分
            "vm_ip": "127.0.0.1",  #虚拟机ip
            "vm_name": "name",  #虚拟机名称
            "question_port": 8080,  #题目开放端口
            "binaryUrl": "http://ai.defcon.ichunqiu.com/resources/fileupload/xxx/bin",   #二进制文件下载地址
            "flag_path": "/home/flag1.txt"  #flag所在地址
        }
    challenge_dict_list = []
    for folder in os.listdir("./local_server/"):
        challenge_dict = copy.copy(challenge_dict_raw) # copy
        challenge_dict["challengeID"] = int(folder)
        challenge_dict["vm_name"] = "vm_name_folder_%s" % unicode(folder)
        challenge_dict["question_port"] = 9000+int(folder)
        challenge_dict["binaryUrl"] = "http://127.0.0.1:5000/resources/fileupload/%s/bin" % unicode(folder)
        challenge_dict["flag_path"] = "/home/t/flag%s.txt" % unicode(folder)
        challenge_dict_list.append(challenge_dict)

    t["AiChallenge"] = challenge_dict_list

    return json.dumps(t)



def answer_check(answer):
    flag_folder = "/home/t/"
    if os.path.exists(flag_folder):
        for folder in os.listdir("./local_server/"):
            flag_path = flag_folder + "/flag%s.txt" % folder
            with open(flag_path,'r')  as f :
                if answer == f.read():
                    return True
        return False
    else:
        print flag_folder + "not exists"
        exit(-1)


# curl  -d "answer=flag" -X POST -v   --user $user:$pwd $URL/api/sub_answer
@app.route('/api/sub_answer', methods=['GET', 'POST'])
def api_sub_answer():
    if request.method == 'POST':
        answer = request.form['answer']
        status = answer_check(answer)
        if status == True :
            t =  {"status": 1, "msg": "success", "questionScore": 128,
                 "questionRank": 1}  # questionScore:得分, questionRank:本次提交题目排名

        elif status == False:
            t = {"status": 0, "msg": "The answer is wrong" }

        return json.dumps(t)
    else:
        return 'sub_answer: should not get'


def reset_ChallengeID(ChallengeID):
    print "reset_ChallengeID %s" % ChallengeID
    return 1

# curl -v -d "ChallengeID=1" -X POST   --user $user:$pwd $URL/api/reset_question
@app.route('/api/reset_question', methods=['GET', 'POST'])
def api_reset_question():
    """
    接口暂未使用
    :return:
    """
    if request.method == 'POST':
        msg = ''
        ChallengeID = request.form['ChallengeID']
        status = reset_ChallengeID(ChallengeID)
        if status == 1 :
            t =  {"status":1,"msg":"success"}

        elif status == 0:
            t = {"status":0,"msg":"提示信息"}

        return json.dumps(t)
    else:
        return 'reset_question: should not get'



# curl  -d "answer=flag" -X POST  -v --user $user:$pwd $URL/api/get_machines_info
@app.route('/api/get_machines_info', methods=['GET', 'POST'])
def api_get_machines_info():
    """
    接口暂未使用
    :return:
    """
    is_running = True # boolean
    t = {
        "name":"test1",   #机器名称
        "questions":[
            {
                "challengeID":18,  #题目id
                "is_running":is_running,  #赛题端口状态
                "connection_number":2  # 进程连接数
            }
        ],
        "virtual_memory":{  # 服务器内存信息
            "available":428322816,  # 已获取内存
            "used":450215936,  # 已使用内存
            "cached":194371584,   # 缓存
            "percent":58.5,   # 百分比
            "free":387031040,  # 剩余内存
            "shared":9244672,  # 共享内存
            "total":1032589312  # 总物理内存
        },
        "cpu":{  # CPU信息
            "physical_count":1,  # 物理数量
            "logical_count":1,  # 逻辑数量
            "percent":21.9   # 资源百分比 0.1/s
        },
        "swap_memory":{  # 交换内存信息
            "used":0,  # 已使用
            "total":2147479552,  # 总量
            "percent":0,  # 百分比
            "free":2147479552   # 剩余
        },
        "process_number":130  # 服务器进程数
    }
    return json.dumps(t)


if __name__ == '__main__':
    # make_flags()
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
