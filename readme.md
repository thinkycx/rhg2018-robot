# README
# 框架运行前注意事项
1. 设置环境变量　参考env.sh: user pwd URL
2. URL若为127.0.0.1 需要运行local_server.py 作为本地服务器
3. AFL module 需要　echo core >/proc/sys/kernel/core_pattern
4. PYCHARM中运行PWNTOOLS需要设置环境变量
    export TERM=linux
    export TERMINFO=/etc/terminfo
5. fuzz部分需要开启debug,需要删除challenges下的文件
6.




# 框架说明
20180425 本框架主要完成 题目获取、fuzz产生崩溃、漏洞利用、提交flag四个部分。


1 首先下载所有题目，初始化challenge_list fuzzrobot_list exprobot_list.
2 检查challenge是否有原题，有原题直接打流量，打成功就设置challenge_list submit_status True,这题不用做了。
（提取５０题的string, 看看是否有和这几题重复的？）　
3 修改challenge_list 顺序
　　- 根据是否是菜单题，菜单题目分数是否考虑降低？
   - 是否需要根据本题的已经做出来的队员数目来降低顺序？可是就３个队伍。128 64 32

检测当前 运行的robot(fuzzrobot_list exprobot_list) 总的数量，
如果小于fuzz_num,就运行新的fuzzrobot。
如果fuzzrobot产生了crash,就停止fuzzrobot，创建exprobot，开始利用。
如果exprobot产生了expflow,就停止exprobot,利用打远程。(list?
如果打成功，就停止fuzzrobot和exprobot,实际上已经停止了？不需要停止了吧？

如果没有产生crash、expflow,超过一定时间就杀掉fuzzrobot和exprobot。
-　考虑增加FUZZ和EXP时间？
-


题目获取模块：
    下载50道题目到本地challenges文件夹下

fuzz模块：
    调用AFL模块对文件夹下每个文件进行fuzz，如果产生新的crash就调用利用模块

漏洞利用模块：
    根据fuzz产生的crash来利用

提交flag：
    提交flag到challenge中的服务器，获取flag后提交，
    如果提交flag成功，kill前两个模块中challengeID对应的进程
        可以


# 文件说明
- api.py   　　　封装了和题目交互的api
- config.py　　　配置文件
- local_server.py　本地模拟的服务器、用来下载本地题目、测试本地题目是否正确
- robot.py　　　　　　核心框架
- requirements.txt　需要的依赖包
- /challenges   下载保存的文件，子目录为challengeid 标识的文件夹，也是fuzz和exploit运行的文件夹
- /local_server 本地服务器模拟的文件夹，保存本地测试的题目

# 本地服务器模拟
    local_server.py　实现了一个简单的比赛服务平台，用来本地测试robot。可以布置测试题目、验证flag是否正确（注意运行的环境得在主办方提供的虚拟机中）。
## 如何发布题目
　　　在local_server新建文件夹，以challengeid命名，题目文件名为bin

# docker
启动image时需要 --privileged
启动后　echo core >/proc/sys/kernel/core_pattern
docker cp 拷贝文件后，测afl.py






# 其他　
其他需要考虑的点：
- 获取积分后，如果分数太低，考虑放弃某些题目？
- (DONE)中间会间断一次，如何保证时间关闭后程序继续fuzz，在开启接口后自动提交。 中间不会断了。
- pycharm 运行时有时候会自动多运行一些aflrobot进程，pycharm写好后，直接用bash运行比较好。20180508



- 20180505 binary_path　是否需要在另外两个类中？
- 获取了流量之后，交互时有问题
- 20180507 是否可以考虑准备好exp　来打？
