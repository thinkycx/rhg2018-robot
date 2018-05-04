
import logging
import os

USER = os.environ.get("RHG_USER")
PWD = os.environ.get("RHG_PWD")
URL = "http://ai.defcon.ichunqiu.com"
# URL = "http://127.0.0.1:5000"
logging.basicConfig( level=logging.WARN)

AFLPATH = '/home/thinkycx/fuzz/afl-2.52b/afl-fuzz'


