#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task dispatch server '

__author__ = 'devilogic'


import sys
import time
import socket
import MySQLdb
from DBUtils.PooledDB import PooledDB

from ns2log import g_ns2log
from ns2tab import *
from ns2tkque import *

DEF_DBPOOL_MAX_SIZE = 20    # db线程池数量
DEF_DBPOOL_MAX_USAGE = 20   # 一条单个链接可以重复使用得最大次数

########################################################################
class Ns2DB:
    """
    娜迦数据库服务器获取类，在这个类中，负责链接数据库，并且提供一个队列，这个队列
    负责存储所有从数据库中读取出来的任务
    """

    #----------------------------------------------------------------------
    def __init__(self, task_max_count=20, block=True, time_out=5):
        """Constructor"""
        g_ns2log.info("娜迦数据库管理模块加载")
        self.task_max_count = task_max_count
        self.task_queue = Ns2TaskQueue(task_max_count, block, time_out)

    #----------------------------------------------------------------------
    def __del__(self):
        """销毁"""
        g_ns2log.info("娜迦数据库管理模块卸载")

    def connect(self, ms=DEF_DBPOOL_MAX_SIZE, mu=DEF_DBPOOL_MAX_USAGE, **info):
        """链接数据库"""
        try:
            # 不限制链接数量
            self.dbpool = PooledDB(MySQLdb, maxshared=ms, maxusage=mu, 
                                   blocking=True, **info)
            return self.dbpool

        except BaseException, e:
            g_ns2log.exception(e.message)
            return None

    #----------------------------------------------------------------------
    def run_sql(self, sql):
        """执行sql语句"""
        if len(sql) == 0:
            return None, None
        try:
            conn = self.dbpool.connection()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            return conn, cur
        except BaseException, e:
            g_ns2log.exception(e.message)
            cur.close()
            conn.close()            
            return None, None

    #----------------------------------------------------------------------
    def get_connect(self):
        """获取链接属性"""
        return self.dbpool.connection()

    #----------------------------------------------------------------------
    def get_self_host(self):
        """获取本地ip,与名称"""
        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)
            return host, ip
        except BaseException, e:
            g_ns2log.exception(e.message)
            return "Unknow", "127.0.0.1"


    #----------------------------------------------------------------------
    def login(self, note=""):
        """向任务数据库登录分发服务器"""
        # 向数据库登录自己的ip, 名字, 以及登录时间
        now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))    # 转换格式
        try:
            self.note = note
            self.hostname, self.ip = self.get_self_host()
            sql = "INSERT INTO login_info (name, ip, note, time) VALUES ('%s', '%s', '%s', '%s')" % (self.hostname, self.ip, self.note, now_time)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            cur.close()
            conn.close()
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def fetch_one_task(self, tid):
        """
        获取sql语句执行后的一个结果,并以数据表字段的方式保存到字典中
        任务返回是一个双元组[]([...],[[]...]),...]
        列表的第一个元素是一个列表[...],其中记录了所有任务表字段
        列表的第二个元素是一个列表[[]...],其中记录了将文件参数队列的服务器信息
        这里缓存了'tid'类型的任务。
        """
        # 获取一条记录
        # 向数据库任务的状态
        try:
            sql = "SELECT id,argv,argv_files FROM tab_task WHERE type = %d AND status = %d" % (tid, NS2_TASK_STATUS.READY)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return None
            
            r = cur.fetchone()
            if r == None:
                return None
            
            cur.close()
            conn.close()            
            
            task_id = r[0]
            argv = r[1]
            argv_files = r[2]
            
            # 设置当前任务进度,与状态
            self.update_task_status(task_id, NS2_TASK_STATUS.CACHE)
            self.update_task_process_bar(task_id, 30)
            
            # 如果存在文件列表, 取出对应得文件信息
            file_park = []
            if argv_files != None:
                file_park = self.get_file_sign_list(argv_files)
                
            # 合成结果
            task_park = (task_id, tid, argv, argv_files)
            task_all = []
            task_all.append(task_park)
            task_all.append(file_park)
            
            # 向任务队列中传递一个
            self.task_queue.put_one_task(tid, task_all)
            return task_all
            
        except BaseException, e:
            g_ns2log.exception(e.message)
            cur.close()
            conn.close()            
            return None

    #----------------------------------------------------------------------
    def fetch_n_task(self, tid, num):
        """
        获取sql语句执行后的n个任务，如果当前任务队列中存在'num'个任务则取出，
        如果没有或者小于则从数据库服务器中取出'self.max_task_count'个,随后
        填补要取的
        """
        if num > self.task_max_count:
            num = self.task_max_count
            
        tasks = []
        try:
            for i in range(num):
                task = self.fetch_one_task(tid)
                if task == None:
                    break
                tasks.append(task)
                return task
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None

    #----------------------------------------------------------------------
    def get_file_info(self, fs):
        """获取文件信息从数据库"""
        try:
            sql = "SELECT * FROM tab_file WHERE sign='%s'" % fs
            conn, cur = self.run_sql(sql)
            if conn == None:
                return None
            
            r = cur.fetchone()
            if r == None:
                return None
            
            cur.close()
            conn.close()
            return r
        except BaseException, e:
            g_ns2log.exception(e.message)
            cur.close()
            conn.close()            
            return None
        

    #----------------------------------------------------------------------
    def get_file_sign_list(self, files):
        """从字符串中取出文件sign的值,并且查询数据库得到对应的信息"""
        try:
            # files 是一个由hash值保存得队列
            result = []
            files = str(files).split(',')
            for f in files:
                # 从数据库中取出相应得信息
                r = self.get_file_info(f)
                if r != None:
                    result.append((f, r))
            return result
        except BaseException, e:
            g_ns2log.exception(e.message)	
            return None


    #----------------------------------------------------------------------
    def update_task_process_bar(self, task_id, process_bar):
        """更新任务进度"""
        try:
            sql = "UPDATE tab_task SET process_bar=%d WHERE id=%d" % (process_bar, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            cur.close()
            conn.close()
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False    
        
    #----------------------------------------------------------------------
    def get_task_rollback(self, task_id):
        """获取回滚次数"""
        try:
            sql = "SELECT rollback_count FROM tab_task WHERE task_id=%d" % task_id
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            rollback = cur.fetchone()
            if rollback == None:
                return None
            
            return int(rollback)
        except BaseException, e:
            g_ns2log.exception(e.message)
            return -1       
        
    #----------------------------------------------------------------------
    def dec_task_rollback_c(self, task_id):
        """任务回滚次数减1"""
        try:
            sql = "SELECT rollback_count FROM tab_task WHERE task_id=%d" % task_id
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            rollback = cur.fetchone()
            if rollback == None:
                return None
            
            rollback = int(rollback)
            
            # 为0直接退出
            if rollback == 0:
                cur.close()
                conn.close()
                return True

            # 减少次数
            rollback = rollback - 1
            
            sql = "UPDATE tab_task SET rollback_count=%d WHERE task_id=%d" % (rollback, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def set_task_completed(self, task_id, v):
        """设置任务已经完成"""
        if v > 0:
            v = 1
        else:
            v = 0
            
        try:
            sql = "UPDATE tab_task SET completed=%d WHERE task_id=%d" % (v, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            cur.close()
            conn.close()
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False	

    #----------------------------------------------------------------------
    def update_task_server_name(self, task_id, srvname):
        """更新任务分发服务器名称"""
        try:
            sql = "UPDATE tab_task SET server_name='%s' WHERE task_id=%d" % (srvname, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False	

    #----------------------------------------------------------------------
    def update_task_status(self, task_id, st):
        """更新任务状态"""
        try:
            sql = "UPDATE tab_task SET status=%d WHERE task_id=%d" % (st, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def update_task_errcode(self, task_id, ec):
        """更新任务出错代码"""
        try:
            sql = "UPDATE tab_task SET errcode=%d WHERE task_id=%d" % (ec, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False	

    #----------------------------------------------------------------------
    def update_task_result(self, task_id, result="", result_files=""):
        """更新任务结果"""
        try:
            sql = "UPDATE tab_task SET result='%s', result_files='%s' WHERE task_id=%d" % (result, result_files, task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False	

    #----------------------------------------------------------------------
    def insert_file_info(self, **info):
        """插入一条文件信息"""
        try:
            sql = "INSERT INTO tab_file (sign, sign_func, host, port, stype, user, passwd, path) VALUE ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (info['sign'], info['sign_func'], info['host'], info['port'], info['stype'], info['user'], info['passwd'], info['path'])
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            cur.close()
            conn.close()
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False	

    #----------------------------------------------------------------------
    def get_task_queue(self):
        """获取任务队列"""
        return self.task_queue
    
    #----------------------------------------------------------------------
    def get_task(self, tid, num=1, retry=False):
        """从任务队列获取任务"""
        return self.task_queue.get_n_task(tid, num, retry)

    #----------------------------------------------------------------------
    def get_task_string(self, tid, num=1, retry=False):
        """获取任务并且格式字符串"""
        tasks = self.get_task(tid, num, retry)
        tasks_string = ""
        for t in tasks:
            ts = "{%d|%s|%s}" % (t[0], t[1], t[2])
            tasks_string += ts
        return tasks_string


if __name__ == '__main__':
    #----------------------------------------------------------------------
    def test():
        """测试单元"""
        dbpool = Ns2DB()
        info = {'host':'172.16.206.133', 
                'user':'root', 
                'passwd':'key123123', 
                'db':'naga_test'}
        pool = dbpool.connect(**info)
        dbpool.login("just test")
        #dbpool.fetch_one_task(1)

    test()