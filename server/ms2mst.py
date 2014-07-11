#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task master server '

__author__ = 'devilogic'

import sys
import time
import threading

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor

import ns2db
import ns2tab
from ns2log import g_ns2log
from ns2ptl import *
from ns2tksrv import *

# 全局变量
global g_tkcltab, g_ns2db

# 客户端锁
g_client_lock = threading.Lock()
#----------------------------------------------------------------------
def new_client(client):
    """新的客户端"""
    try:
        g_client_lock.acquire()
        list(g_tkcltab[client_id]).append(client_value)
    except BaseException, e:
        g_ns2log.exception(e.message)
    finally:
        g_client_lock.release()
        
#----------------------------------------------------------------------
def del_client_by_hostport(hostport):
    """删除客户端"""
    try:
        g_client_lock.acquire()
        for tt in g_tkcltab:
            array = g_tkcltab[tt]
            dict(array).
        list().append(client_value)
    except BaseException, e:
        g_ns2log.exception(e.message)
    finally:
        g_client_lock.release()
        
#----------------------------------------------------------------------
def find_client_by_hostport(hostport):
    """通过ip＋端口寻找客户端"""
    
    
    

########################################################################
class Ns2Master(Factory):
    """用于响应客户端发来的包"""
    protocol = Ns2Protocol

    #----------------------------------------------------------------------
    def __init__(self):
        """初始化"""
        g_ns2log.info("娜迦工厂模块启动")
        g_tkcltab = {}

    #----------------------------------------------------------------------
    def __del__(self):
        """析构函数"""
        pass


    #----------------------------------------------------------------------
    def add_client(self, client):
        """增加客户端,任务类型:主机名:PID:TID"""
        client = str(client).split(":")
        if len(client) != 4:  	    # 出错
            return None
        try:
            client_id = int(client[0])
            client_sign = "%s-%d-%d" % (client[1], client[2], client[3])
            client_address = "%s:%d" % (self.transport.client[0], self.transport.client[1])
            client_value[client_address] = client_sign
            
            
            
            
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None

    #----------------------------------------------------------------------
    def del_client(self):
        """当客户端丢失时调用，用于删除客户端"""
        pass
        

    #----------------------------------------------------------------------
    def put_task(self):
        """下发任务"""
        pass


########################################################################
class Ns2Protocol(LineOnlyReceiver):
    """ns2协议"""

    #----------------------------------------------------------------------
    def connectionLost(self, reason):
        """链接丢失时调用,从任务类型-客户端列表中删除对应的客户端"""
        self.factory.delClient()
        pass


    #----------------------------------------------------------------------
    def connectionMade(self):
        """链接时调用"""
        g_ns2log.info("有新的客户端链接")
        pass

    #----------------------------------------------------------------------
    def lineReceived(self, line):
        """接收到一行数据时调用,以'\r\n'结尾的行
        [命令]:[出错代码]:[返回的一些结果,根据命令不同而不同]
        命令与出错代码必须存在,而数据不一定存在。
        [命令]
        客户端注册                  1
        客户端请求任务               2
        客户端完成任务第一阶段        3
        客户端完成任务第二阶段        4
        """
        try:
            g_ns2log.info("接收到数据 : %s" % line)
            command = get_command(line)
            errcode = get_errcode(line)
            sok = True

            if ns2_success(errcode) == False:
                g_ns2log.error("接收到错误代码 : (%s)%x" % ns2tab.ns2_error_string(errcode), errcode)
                sok = False

            if command == CLIENT_LOGIN:
                if sok == False:
                    return
                
                client_info = get_data(line)
                self.factory.add_client(client_info)
            else if command == CLIENT_REQUEST_TASK:
                if sok == False:
                    return
                
                # 从接受端反查任务类型
                task_type = 0
                task_num = int(get_data(line))     # 获取任务数量
                
                # 从任务队列重获取
                tasks = g_ns2db.get_task_string(task_type, task_num)
                # 发送给客户端
                tasks += "\r\n"
                
            else if command == CLIENT_TASK_COMPLETED_1:
                # 任务没有执行成功
                if sok == False:
                    # 查看当前任务回滚次数,如果不为0则直接
                    pass
            
            else if command == CLIENT_TASK_COMPLETED_2:
                pass
        except BaseException, e:
            g_ns2log.exception(e.message)
            g_ns2log.info("娜迦协议处理模块接收数据出错")





if __name__ == '__main__':
    #----------------------------------------------------------------------
    def test():
        pass

    test()