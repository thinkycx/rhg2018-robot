# README
# 使用方法
1. 设置环境变量　参考env.sh: user pwd URL
2. URL若为127.0.0.1 需要运行local_server.py 作为本地服务器



# 框架说明
20180425 本框架主要完成 题目获取、fuzz产生崩溃、漏洞利用、提交flag四个模块。
针对每一个题目，后续三个模块需要调用多次

题目获取模块：
    下载50道题目到本地challenges文件夹下

fuzz模块：
    调用AFL模块对文件夹下每个文件进行fuzz


漏洞利用模块：
    challengeID标识

提交flag：
    提交flag到challenge中的服务器，获取flag后提交，
    如果提交flag成功，kill前两个模块中challengeID对应的进程
        可以


# 文件说明
- api.py
- config.py
- local_server.py
- robot.py
- requirements.txt
- /challenges   下载保存的文件，fuzz和exploit运行的文件夹
- /local_server 本地服务器模拟

# 本地服务器模拟
    local_server.py　实现了一个简单的比赛服务平台，用来本地测试robot。可以布置测试题目、验证flag是否正确（注意运行的环境得在主办方提供的虚拟机中）。
## 如何发布题目
　　　在local_server新建文件夹，以challengeid命名，题目文件名为bin

# 其他　
其他需要考虑的点：
- 获取积分后，如果分数太低，考虑放弃某些题目？
- 中间会间断一次，如何保证时间关闭后程序继续fuzz，在开启接口后自动提交。

# TIMELINE
- 20180415 api.py 实现对网站函数的封装
