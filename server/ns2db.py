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
from ns2ptl import *
from ns2tab import *
from ns2tkque import *

DEF_DBPOOL_MAX_SIZE = 20    # db线程池数量
DEF_DBPOOL_MAX_USAGE = 20   # 一条单个链接可以重复使用得最大次数
DEF_DBPOOL_STARTUP_CONNECT = 20 # 在启动时就链接的数量

########################################################################
class Ns2DB:
    """
    娜迦数据库服务器获取类，在这个类中，负责链接数据库，并且提供一个队列，这个队列
    负责存储所有从数据库中读取出来的任务
    """

    #----------------------------------------------------------------------
    def __init__(self, task_max_count=20, block=True, time_out=5, retry_it=True, retry_time_out=0):
        """Constructor"""
        g_ns2log.info("娜迦数据库管理模块加载")
        self.retry_it = retry_it
        self.task_max_count = task_max_count
        self.task_queue = Ns2TaskQueue(task_max_count, block, time_out, retry_time_out)

    #----------------------------------------------------------------------
    def __del__(self):
        """销毁"""
        g_ns2log.info("娜迦数据库管理模块卸载")

    def connect(self, mic=DEF_DBPOOL_STARTUP_CONNECT, ms=DEF_DBPOOL_MAX_SIZE, mu=DEF_DBPOOL_MAX_USAGE, **info):
        """链接数据库"""
        try:
            # 不限制链接数量
            self.dbpool = PooledDB(MySQLdb, mincached=mic, maxshared=ms, maxusage=mu, 
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
            sql = "INSERT INTO %s (%s, %s, %s, %s) VALUES ('%s', '%s', '%s', '%s')" % (NS2_LOGIN_INFO_TAB.table_name,
                                                                                       NS2_LOGIN_INFO_TAB.login_tab[NS2_LOGIN_INFO_TAB.NAME],
                                                                                       NS2_LOGIN_INFO_TAB.login_tab[NS2_LOGIN_INFO_TAB.IP],
                                                                                       NS2_LOGIN_INFO_TAB.login_tab[NS2_LOGIN_INFO_TAB.NOTE],
                                                                                       NS2_LOGIN_INFO_TAB.login_tab[NS2_LOGIN_INFO_TAB.TIME],
                                                                                       self.hostname, 
                                                                                       self.ip, 
                                                                                       self.note, 
                                                                                       now_time)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            
            

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
            sql = "SELECT %d,%s,%s FROM %s WHERE %s = %d AND %s = %d" % (NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ARGV],
                                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ARGV_FILES],
                                                                         NS2_TASK_TAB.table_name,
                                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TYPE],
                                                                         tid, 
                                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.STATUS],
                                                                         NS2_TASK_STATUS.READY)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return None
            
            r = cur.fetchone()
            if r == None:
                return None
            
            task_id = r[0]
            argv = r[1]
            argv_files = r[2]
            
            # 设置当前任务进度,与状态
            #self.update_task_status(task_id, NS2_TASK_STATUS.CACHE)
            #self.update_task_process_bar(task_id, g_ns2_status_process[NS2_TASK_STATUS.CACHE])
            self.update_task_status_processbar(task_id, NS2_TASK_STATUS.CACHE)
            
            # 如果存在文件列表, 取出对应得文件信息
            file_park = []
            if argv_files != None:
                file_park = self.get_file_sign_list(argv_files)
                
            # 合成结果
            task_park = (task_id, tid, argv)
            task_all = (task_park, file_park)
            
            # 向任务队列中传递一个
            self.task_queue.put_one_task(tid, task_all, self.retry_it)
            return task_all
            
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None
        finally:
            cur.close()
            conn.close()            

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
            sql = "SELECT %s,%s,%d,%s,%s,%s FROM %s WHERE %s='%s'" % (NS2_FILE_INFO.file_tab[NS2_FILE_INFO.SIGN],
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.HOST],
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PORT],
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.USER],
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PASSWD],
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PATH],
                                                                      NS2_FILE_INFO.table_name,
                                                                      NS2_FILE_INFO.file_tab[NS2_FILE_INFO.SIGN],
                                                                      fs)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return None
            
            r = cur.fetchone()
            if r == None:
                return None
            
            return r
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None
        finally:
            cur.close()
            conn.close()
        

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
                    result.append(r)
            return result
        except BaseException, e:
            g_ns2log.exception(e.message)	
            return None


    #----------------------------------------------------------------------
    def update_task_processbar(self, task_id, process_bar):
        """更新任务进度"""
        try:
            sql = "UPDATE %s SET %s=%d WHERE %s=%d" % (NS2_TASK_TAB.table_name,
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.PROCESS_BAR],
                                                       process_bar, 
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                       task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            
        
    #----------------------------------------------------------------------
    def get_task_rollback(self, task_id):
        """获取回滚次数"""
        try:
            sql = "SELECT %s FROM %s WHERE %s=%d" % (NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ROLLBACK_COUNT],
                                                     NS2_TASK_TAB.table_name,
                                                     NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                     task_id)
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
        finally:
            cur.close()
            conn.close()            
        
    #----------------------------------------------------------------------
    def dec_task_rollback_c(self, task_id):
        """任务回滚次数减1"""
        try:
            sql = "SELECT %s FROM %s WHERE %s=%d" % (NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ROLLBACK_COUNT],
                                                     NS2_TASK_TAB.table_name,
                                                     NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                     task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
            
            rollback = cur.fetchone()
            if rollback == None:
                return None
            
            rollback = int(rollback)
            
            # 为0直接退出
            if rollback == 0:
                return True

            # 减少次数
            rollback = rollback - 1
            
            sql = "UPDATE %s SET %s=%d WHERE %s=%d" % (NS2_TASK_TAB.table_name,
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ROLLBACK_COUNT],
                                                       rollback, 
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                       task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()

    #----------------------------------------------------------------------
    def update_task_client_name(self, task_id, client_name):
        """更新任务客户端名称"""
        try:
            sql = "UPDATE %s SET %s='%s' WHERE %s=%d" % (NS2_TASK_TAB.table_name,
                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.CLIENT_NAME],
                                                         client_name,
                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                         task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()

    #----------------------------------------------------------------------
    def get_task_status(self, task_id):
        """获取任务状态"""
        try:
            sql = "SELECT %s FROM %s WHERE %s=%d" % (NS2_TASK_TAB.task_tab[NS2_TASK_TAB.STATUS],
                                                     NS2_TASK_TAB.table_name,
                                                     NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                     task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
            
            r = cur.fetchone()
                        
            return int(r)
        except BaseException, e:
            g_ns2log.exception(e.message)
            return NS2_TASK_STATUS.UNKNOW_TYPE
        finally:
            cur.close()
            conn.close()

    #----------------------------------------------------------------------
    def update_task_status(self, task_id, st):
        """更新任务状态"""
        try:
            sql = "UPDATE %s SET %s=%d WHERE %s=%d" % (NS2_TASK_TAB.table_name,
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.STATUS],
                                                       st,
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                       task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
                        
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            
        
    #----------------------------------------------------------------------
    def update_task_status_processbar(self, task_id, st):
        """更新任务状态以及进度条"""
        if st < 0:
            raise ValueError("st must be >= 0")
        elif st >= NS2_TASK_STATUS.UNKNOW_TYPE:
            raise ValueError("st must be < %d" % NS2_TASK_STATUS.UNKNOW_TYPE)
        
        self.update_task_status(task_id, st)
        self.update_task_processbar(task_id, ns2tab.g_ns2_status_process[st])

    #----------------------------------------------------------------------
    def update_task_errcode(self, task_id, ec):
        """更新任务出错代码"""
        try:
            sql = "UPDATE %s SET %s=%d WHERE %s=%d" % (NS2_TASK_TAB.table_name,
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.ERROR_CODE],
                                                       ec, 
                                                       NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                       task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False            
                        
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            

    #----------------------------------------------------------------------
    def update_task_result(self, task_id, result=""):
        """更新任务结果"""
        try:
            sql = "UPDATE %s SET %s='%s', WHERE %s=%d" % (NS2_TASK_TAB.table_name, 
                                                          NS2_TASK_TAB.task_tab[NS2_TASK_TAB.RESULT],
                                                          result, 
                                                          NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                          task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
                        
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close() 
            
    #----------------------------------------------------------------------
    def update_task_result_files(self, task_id, result_files=""):
        """更新任务结果"""
        try:
            sql = "UPDATE %s SET %s='%s' WHERE %s=%d" % (NS2_TASK_TAB.table_name, 
                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.RESULT_FILES],
                                                         result_files, 
                                                         NS2_TASK_TAB.task_tab[NS2_TASK_TAB.TASK_ID],
                                                         task_id)
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
                        
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            
        
        
    #----------------------------------------------------------------------
    def insert_file_info(self, info):
        """插入一条文件信息"""
        try:
            sql = "INSERT INTO %s (sign, host, port, user, passwd, path) VALUE ('%s', '%s', '%s', '%s', '%s', '%s')" % (NS2_FILE_INFO.table_name,
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.SIGN],
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.HOST],
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PASSWD],
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.USER],
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PASSWD],
                                                                                                                        NS2_FILE_INFO.file_tab[NS2_FILE_INFO.PATH],
                                                                                                                        info[0], 
                                                                                                                        info[1], 
                                                                                                                        info[2], 
                                                                                                                        info[3], 
                                                                                                                        info[4], 
                                                                                                                        info[5])
            conn, cur = self.run_sql(sql)
            if conn == None:
                return False
                        
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            cur.close()
            conn.close()            
        
    #----------------------------------------------------------------------
    def insert_files_info(self, files):
        """插入n条文件信息"""
        try:
            for f in files:
                self.insert_files_info(f)
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def get_task_queue(self):
        """获取任务队列"""
        return self.task_queue
    
    #----------------------------------------------------------------------
    def get_task(self, tid, num=1, client_name=""):
        """从任务队列获取任务"""
        tasks = self.task_queue.get_n_task(tid, num, self.retry_it)
        for t in tasks:
            task_id = t[0][0]
            
            # 更新客户端名称与进度
            self.update_task_client_name(task_id, client_name)
            self.update_task_status_processbar(task_id, NS2_TASK_STATUS.PROCESS)
        return tasks
    
    #----------------------------------------------------------------------
    def get_task_string(self, tid, num=1, client_name=""):
        """获取任务并且格式字符串"""
        tasks = self.get_task(tid, num, client_name)  # 这是一个二元组
        tasks_string = ""
        for t in tasks:
            task_park = t[0]   # 三元组
            file_park = t[1]   # 队列[()]
            
            # 任务与任务之间用 ';' 号隔开, 任务与文件之间用 '#'号隔开, 文件值与任务值之间用 '|'分割
            ts = "%d|%s|%s" % (task_park[0], task_park[1], task_park[2])   # 任务部分
            for one_file in file_park:
                #sign,host,port,stype,user,passwd,path
                fs += "%s|%s|%d|%d|%s|%s|%s;" % (one_file[0], one_file[1], one_file[2], 
                                                 one_file[3], one_file[4], one_file[5],
                                                 one_file[6])
            one_task = "%s#%s," % (ts, fs)
            tasks_string += one_task
            
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