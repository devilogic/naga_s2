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
from ns2tkcltab import g_tkcltab
from ns2db import *
from ns2mst import *

# 任务类型-客户端对应表
global g_dbpool, g_ns2db

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
        if self.master_thread.wait_connect_sql(500) == False:
            return False
        
        try:
            # 读取配置项目，并启动客户端控制服务器
            config = ConfigParser.ConfigParser()
            config.read('server.ini')
            bindport = config.getint("SERVER", "bindport")  # 读取服务器的端口
            g_ns2log.info("开启客户端控制服务器，监听端口:%d\n" % (bindport))

            # 运行任务分发服务器
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
        self.retry_mode = False
        self.retry_time_out = 0
        self.time_out = 0
        self.__conn_sql_flag = False
        self.wait_event = threading.Event()

    #----------------------------------------------------------------------
    def __del__(self):
        """模块销毁"""
        g_ns2log.info("娜迦数据库查询模块卸载")


    #----------------------------------------------------------------------
    def wait_connect_sql(self, time_out=1):
        """等待链接"""
        self.wait_event.wait(time_out)
        return self.get_connect_sql_result()

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
            self.block_mode = config.getboolean("CONTROL", "block_mode") # 是否是阻塞模式
            self.time_out = config.getint("CONTROL", "time_out") # 超时设定
            self.retry_mode = config.getboolean("CONTROL", "retry_mode") # 是否是阻塞模式
            self.retry_time_out = config.getint("CONTROL", "retry_time_out") # 如果获取或者设置任务超时则是否重新进入
            self.rollback_failed_handle = config.getint("CONTROL", "rollback_failed_handle")
            if self.rollback_failed_handle < 0:
                self.rollback_failed_handle = 0
            
            # 预先获取任务
            pre_tasks = config.get("CONTROL", "pre_tasks") 
            self.pre_tasks = []
            if pre_tasks != '':
                pre_tasks = pre_tasks.split(',')
                for i in range(len(pre_tasks)):
                    task_id = int(pre_tasks[i])
                    self.pre_tasks.append(task_id)

            # 启动任务数据管理
            self.ns2db = Ns2DB(self.max_task, self.block_mode, self.time_out, self.retry_mode, self.retry_time_out)
            g_ns2db = self.ns2db

            # 链接 --- mysql
            connect_info = {}
            connect_info = {'host':'172.16.206.133',
                            'user':'root', 
                            'passwd':'key123123', 
                            'db':'naga_test'}
            #connect_info['host'] = ip
            #connect_info['user'] = username
            #connect_info['passwd'] = pwd
            #connect_info['db'] = dbname
            self.dbpool = self.ns2db.connect(**connect_info)
            if self.dbpool == None:
                self.__conn_sql_flag = False
                g_ns2log.info("链接娜迦任务数据库失败")
                return False
            else:
                g_ns2log.info("链接娜迦任务数据库成功")
            g_dbpool = self.dbpool

            # 向任务数据库登录自己
            if g_ns2db.login(note) == True:
                self.__conn_sql_flag = True
                g_ns2log.info("登录娜迦任务数据库成功")
                return True 

            else:
                self.__conn_sql_flag = False
                g_ns2log.info("登录娜迦任务数据库失败")
                return False
        except BaseException, e:
            g_ns2log.info("链接娜迦任务数据库失败")
            g_ns2log.exception(e.message)
            self.__conn_sql_flag = False
            return False
        finally:
            self.wait_event.set()      # 通知可以继续运行了
            

    #----------------------------------------------------------------------
    def get_connect_sql_result(self):
        """获取链接数据库结果"""
        return self.__conn_sql_flag


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
            if len(g_tkcltab):
                # i是任务类型
                tlist = g_tkcltab.get_task_id_list()
                for i in tlist:
                    self.ns2db.fetch_n_task(int(i), self.max_task)
                    
        except BaseException, e:
            g_ns2log.exception(e.message)

    #----------------------------------------------------------------------
    def run(self):
        """如果链接失败,或者链接已经断开"""
        
        # 连接数据库
        ret = self.connect_mysql()
        if ret == False:
            return
        
        while os.path.isfile('run.ns2'):
            self.refresh()    # 更新任务
            time.sleep(self.refresh_time)


if __name__ == '__main__':
    #----------------------------------------------------------------------
    def main():
        """测试单元"""
        tasksrv = Ns2TaskServer()
        tasksrv.Start()

    main()