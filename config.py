
import logging
import os

USER = os.environ.get("RHG_USER")
PWD = os.environ.get("RHG_PWD")
URL = os.environ.get("URL")
# URL = "http://ai.defcon.ichunqiu.com"
# URL = "http://127.0.0.1:5000"
# URL = "http://172.16.4.110"

logging.basicConfig( level=logging.WARN)

afl_path_docker = '/root/rhg2018-robot/afl-2.52b/afl-fuzz'
# temporarily fix detech docker problem
afl_path_local = '/root/rhg2018-robot/afl-2.52b/afl-fuzz'
# afl_path_local = '/home/thinkycx/fuzz/afl-2.52b/afl-fuzz'


