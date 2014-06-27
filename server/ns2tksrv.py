#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task dispatch server '

__author__ = 'devilogic'

import sys
import time
import ConfigParser
import Queue
import ns2db
import ns2log

# --------------------------------------------------
# 全局变量区域
# --------------------------------------------------
g_ns2db = ns2db.Ns2DB()
g_task_queue = Queue.Queue()

# --------------------------------------------------
# 任务分发服务器类
# --------------------------------------------------
class TaskServer():
    # 初始化一个工作线程管理类
    def __init__(self):
	self.query_thread = QueryWorkItemThread("query task thread")

    # 析构函数检查队列中是否还有线程活动
    def __del__(self):
	# 如果线程还在执行,则等待
	if self.query_thread.isAlive():
	    self.query_thread.join()			
	print("TaskServer del\n")

    # 启动服务
    def Start(self):
	# 链接数据库
	if self.query_thread.connect_mysql():
	    self.query_thread.start()  # 启动任务查询线程
	    # 读取配置项目
	    config = ConfigParser.ConfigParser()
	    config.read('server.ini')
	    bindport = config.getint("SERVER", "bindport")  # 读取服务器的端口
	    print "bind port %s\n" % (bindport)

	    # 运行任务分发服务器
	    #reactor.listenTCP(bindport, ClientRecverFactory())
	    #reactor.run()           
	else:
	    print "[-]connect to task database failed\n"

# 线程工作类
class QueryWorkItemThread(threading.Thread):
    # 初始化	
    def __init__(self, threadname):
	threading.Thread.__init__(self, name = threadname)
	self.max_task = 100
	self.refresh_time = 5
	self.sleep_time = 1

    # 链接mysql数据库
    def connect_mysql(self):
	print "connecting task db ...."
	try:  
	    config = ConfigParser.ConfigParser()
	    config.read('server.ini')

	    # 获取服务器自身属性
	    note = config.get("INFO", "note")

	    # 链接任务数据库配置
	    ip =  config.get("DATABASE", "ip")       # 数据库服务器ip
	    username = config.get("DATABASE", "user")  # 用户名
	    pwd = config.get("DATABASE", "passwd")     # 密码
	    dbname = config.get("DATABASE", "db")      # 数据库名称

	    # 获取配置
	    self.max_task = config.getint("CONTROL", "max_task")  # 任务队列最大数量
	    self.refresh_time = config.getint("CONTROL", "refresh_time") # 任务刷新时间
	    self.sleep_time = config.getint("CONTROL", "sleep_time") # 获取睡眠时间

	    # 链接 --- mysql
	    self.conn = g_ns2db.connect(host=ip, user=username, password=pwd, 
	                                database=dbname, use_unicode=True)

	    # 向任务数据库登录自己
	    if g_ns2db.login(note) == True:
		print("connet task db sucess")
		return True
	    else:
		print("connet task db failed")
		return False
	except:
	    # 链接数据库异常记录到日志
	    return False

    # 更新任务队列
    def fetch_tasks(self):
	try:
	    curr_task_list = g_ns2db.fetch_n_task(self.max_task)
	    if len(curr_task_list):
		for curr in curr_task:
		    g_task_queue.put(curr)
	except Full, e:
	    pass


    # 任务更新函数
    def refresh(self):
	try:
	    # 更新任务队列
	    fetch_tasks()
	    time.sleep(self.sleep_time)
	except:
	    # 发生异常后,记录到日志
	    pass

    # 更新任务线程函数
    def run(self):
	while True:
	    # 更新工作队列
	    refresh()
	    time.sleep(self.refresh_time)

# 测试
#----------------------------------------------------------------------
def test():
    """测试"""
    pass


if __name__ == 'main':
    test()