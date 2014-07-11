#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task dispatch server '

__author__ = 'devilogic'

import os
import sys
import time
import ConfigParser
import threading
from twisted.internet import reactor

from ns2log import g_ns2log
from ns2db import *
from ns2mst import *

# 任务类型-客户端对应表
global g_tkcltab, g_dbpool, g_ns2db
# --------------------------------------------------
# 任务分发服务器类
# --------------------------------------------------
class Ns2TaskServer():
    """启动"""
    #----------------------------------------------------------------------
    def __init__(self):
	"""初始化一个工作线程管理类"""
	g_ns2log.info("娜迦任务分发服务模块加载")
	self.master_thread = Ns2QueryThread("master")

    #----------------------------------------------------------------------
    def __del__(self):
	"""析构函数检查队列中是否还有线程活动"""
	g_ns2log.info("娜迦任务分发服务模块卸载")
	# 如果线程还在执行,则等待
	if self.master_thread.isAlive():
	    self.master_thread.join()

    #----------------------------------------------------------------------
    def Start(self):
	"""启动服务"""
	self.master_thread.start()  # 启动任务查询线程

	try:
	    # 读取配置项目，并启动客户端控制服务器
	    config = ConfigParser.ConfigParser()
	    config.read('server.ini')
	    bindport = config.getint("SERVER", "bindport")  # 读取服务器的端口
	    g_ns2log.info("开启客户端控制服务器，监听端口:%d\n" % (bindport))

	    # 运行任务分发服务器
	    dbpool = self.master_thread.get_taskdb()
	    reactor.listenTCP(bindport, Ns2Master())
	    reactor.run()

	    g_ns2log.info("娜迦任务分发服务模块启动成功")
	    return True
	except BaseException, e:
	    g_ns2log.info("娜迦任务分发服务模块启动失败")
	    g_ns2log.exception(e.message)
	    return False

class Ns2QueryThread(threading.Thread):
    """线程工作类"""
    #----------------------------------------------------------------------
    def __init__(self, threadname):
	"""初始化"""
	g_ns2log.info("娜迦数据库查询模块加载")
	threading.Thread.__init__(self, name = threadname)
	self.max_task = 100
	self.refresh_time = 5
	self.force_gettask = 0
	self.pre_tasks = []
	self.rollback_failed_handle = 0    # 0:表示丢弃, 1表示重置

    #----------------------------------------------------------------------
    def __del__(self):
	"""模块销毁"""
	g_ns2log.info("娜迦数据库查询模块卸载")


    #----------------------------------------------------------------------
    def connect_mysql(self):
	"""链接mysql数据库"""
	g_ns2log.info("正在娜迦链接任务数据库...")

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
	    self.force_task = config.getboolean("CONTROL", "force_task") # 获取睡眠时间
	    # 预先获取任务
	    pre_tasks = config.get("CONTROL", "pre_tasks") 
	    self.pre_tasks = []
	    if pre_tasks != '':
		pre_tasks = pre_tasks.split(',')
		for i in rang(len(pre_tasks)):
		    self.pre_tasks[i] = int(pre_tasks[i])
	    self.rollback_failed_handle = config.getint("CONTROL", "rollback_failed_handle")
	    if self.rollback_failed_handle < 0:
		self.rollback_failed_handle = 0

	    # 启动任务数据管理
	    self.ns2db = Ns2DB(self.max_task, self.block_task, self.time_out_task)
	    g_ns2db = self.ns2db

	    # 链接 --- mysql
	    g_dbpool = self.ns2db.connect(host=ip, user=username, password=pwd, 
	                                  database=dbname, use_unicode=True)
	    if g_dbpool == None:
		g_ns2log.info("链接娜迦任务数据库失败")
		return False
	    else:
		g_ns2log.info("链接娜迦任务数据库成功")
	    self.dbpool = g_dbpool

	    # 向任务数据库登录自己
	    if g_ns2db.login(note) == True:
		g_ns2log.info("登录娜迦任务数据库成功")
		return True 

	    else:
		g_ns2log.info("登录娜迦任务数据库失败")
		return False
	except BaseException, e:
	    g_ns2log.info("链接娜迦任务数据库失败")
	    g_ns2log.exception(e.message)
	    return False

    #----------------------------------------------------------------------
    def get_taskdb(self):
	"""返回任务数据库"""
	return self.dbpool


    #----------------------------------------------------------------------
    def refresh(self):
	"""刷新任务"""
	try:
	    # 检查是否需要强制获取任务表
	    if self.force_gettask == True:
		if len(self.pre_tasks):
		    for i in range(self.pre_tasks):
			self.ns2db.fetch_n_task(self.pre_tasks[i], 
			                        self.max_task)

	    # 检索任务类型-客户端对应表,如果表中有数据则获取任务
	    if len(self.tkcltab):
		# 这里使用dict进行迭代
		for i in g_tkcltab:
		    tc = g_tkcltab[i]
		    tid = tc[0]
		    clients = tc[1]       # 取出客户端队列
		    clients_count = len(clients)
		    # 如果客户端为0,则丢弃这个
		    if clients_count == 0:
			g_tkcltab.pop(i)
		    # 有多少客户的就取多少次
		    for j in range(clients_count):
			self.ns2db.fetch_n_task(tid, self.max_task)

	except BaseException, e:
	    g_ns2log.exception(e.message)

    #----------------------------------------------------------------------
    def run(self):
	"""如果链接失败,或者链接已经断开"""
	while os.path.isfile('run.ns2'):
	    refresh()    # 更新任务
	    time.sleep(self.refresh_time)


if __name__ == '__main__':
    #----------------------------------------------------------------------
    def test():
	"""测试单元"""
	pass

    test()