#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
import config
import os


USER = config.USER
PWD  = config.PWD

URL = config.URL
GET_QUESTION_STATUS = URL + "/api/get_question_status"
GET_MACHINES_INFO = URL + "/api/get_machines_info"
RESET_QUESTION = URL + "/api/reset_question"
SUB_ANSWER = URL + "/api/sub_answer "

headers = {'User-Agent': 'curl / 7.47.0'}

#,
#        'Authorization': 'Basic dXNlcjAyOjhzdXlxQw==',
#
def get_question_status():
    try:
        r = requests.get(url=GET_QUESTION_STATUS, auth=(USER, PWD), headers=headers)
        return r.json()['AiChallenge']
    except Exception as e:
        logging.error(e)
        return False


def get_machines_info():
    try:
        r = requests.get(url=GET_MACHINES_INFO, auth=(USER, PWD), headers=headers)
        print r.json()
        return r.json()
    except Exception as e:
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
        logging.info(unicode(e))
        exit(-1)


if __name__ == "__main__":
    get_machines_info()


