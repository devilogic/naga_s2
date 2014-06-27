#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task dispatch server '

__author__ = 'devilogic'


from ns2log import *
from ns2tab import *
import mysql.connector
import sys
import socket
import Queue

########################################################################
class Ns2DB:
    """naga server 2 database control"""

    #----------------------------------------------------------------------
    def __init__(self, task_max_size=20):
	"""Constructor"""
	self.task_queue = 
	pass

    def connect(self, **info):
	"""链接数据库"""
	try:
	    self.conn = mysql.connector.connect(info)
	    return self.conn
	except:
	    return None

    #----------------------------------------------------------------------
    def run_sql(self):
	"""执行sql语句"""
	try:
	    conn = self.conn
	    cur = conn.cursor()
	    cur.execute(sql)
	    conn.commit()
	    return conn

	except:
	    return None	


    #----------------------------------------------------------------------
    def run_sql2(self, sql):
	"""执行sql语句并关闭链接"""
	try:
	    conn = self.conn
	    cur = conn.cursor()
	    cur.execute(sql)
	    conn.commit()
	    return 0

	except:
	    pass

	finally:
	    cur.close()
	    conn.close()
	    return -1

    #----------------------------------------------------------------------
    def get_connect(self):
	"""获取链接属性"""
	return self.conn

    #----------------------------------------------------------------------
    def get_self_host(self):
	"""获取本地ip,与名称"""
	try:
	    host = socket.gethostname()
	    ip = socket.gethostbyname(host)
	    return host, ip
	except:
	    return "Unknow", "127.0.0.1"
	

    #----------------------------------------------------------------------
    def login(self, note=""):
	"""向任务数据库登录分发服务器"""
	# 向数据库登录自己的ip, 名字, 以及登录时间
	try:
	    self.note = note
	    host, ip = get_self_ip()
	    return True
	except:
	    return False

    #----------------------------------------------------------------------
    def fetch_one_task(self):
	"""
	获取sql语句执行后的一个结果,并以数据表字段的方式保存到字典中
	任务返回是一个双元组[]([...],[[]...]),...]
	列表的第一个元素是一个列表[...],其中记录了所有任务表字段
	列表的第二个元素是一个列表[[]...],其中记录了将文件参数队列的服务器信息
	"""
	# 获取一条记录
	# 向数据库任务的状态
	pass

    #----------------------------------------------------------------------
    def fetch_n_task(self, num):
	"""获取sql语句执行后的n个结果,并以数据表字段的方式保存到字典中"""
	pass

    #----------------------------------------------------------------------
    def fetch_all_task(self):
	"""获取sql语句执行后的所有结果,并以数据表字段的方式保存到字典队列中"""
	pass

    #----------------------------------------------------------------------
    def get_file_sign_list(self, files):
	"""从字符串中取出文件sign的值,并且查询数据库得到对应的信息"""
	pass

    
    #----------------------------------------------------------------------
    def update_task_info(self, **info):
	"""更新任务状态"""
	try:
	    if info[NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ID]] == 0:
		return False
	    else:
		# 合成sql语句
		return True
	except:
	    pass

    #----------------------------------------------------------------------
    def dec_task_rollback_c(self, tid):
	"""任务回滚次数减1"""
	pass
    
    #----------------------------------------------------------------------
    def set_task_completed(self, tid):
	"""设置任务已经完成"""
	pass
    
    #----------------------------------------------------------------------
    def update_task_server_name(self, srvname):
	"""更新任务分发服务器名称"""
	pass
    
    #----------------------------------------------------------------------
    def update_task_status(self, tid, st):
	"""更新任务状态"""
	pass

    def update_task_errcode(self, tid, ec):
	"""更新任务出错代码"""
	pass

    #----------------------------------------------------------------------
    def update_task_result(self, tid, result="", result_file=""):
	"""更新任务结果"""
	pass
	
    #----------------------------------------------------------------------
    def insert_file_info(self, **info):
	"""插入一条文件信息"""
	pass
    
    #----------------------------------------------------------------------
    def get_task_queue(self):
	"""获取任务队列"""
	return self.task_queue
	
	

if __name__ == '__main__':
    main()