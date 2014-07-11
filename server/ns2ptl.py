# -*- coding: utf-8 -*-

' naga task server protocol '

__author__ = 'devilogic'


from ns2ptl import *
from ns2log import g_ns2log

########################################################################
class NS2_CLIENT_COMMAND:
    """客户端向服务器发送的命令"""
    CLIENT_LOGIN = 0x10000001                  # 数据为客户端信息
    CLIENT_REQUEST_TASK = 0x10000002           # 数据为具体要获取的任务数量
    CLIENT_TASK_COMPLETED_1 = 0x10000003       # 无数据
    CLIENT_TASK_COMPLETED_2 = 0x10000004       # 按照具体情况，如果存在即存放入数据库的result字段

########################################################################
class NS2_SERVER_COMMAND:
    """服务器向客户端发送的命令"""
    SERVER_TASK_READY = 0x20000001             # 数据区域就是任务列表
    SERVER_TASK_GO_NEXT = 0x20000002           # 无数据
    SERVER_TASK_IGNORE = 0x20000003            # 无数据
    
    
#----------------------------------------------------------------------
def make_command(cmd, errcode, data):
    """合成一个命令字符串"""
    command = "%x:%x:%s\r\n" % (cmd, errcode, data)
    return command

#----------------------------------------------------------------------
def get_command(command):
    """获取命令部分"""
    try:
        s = str(command).split(":")
        if len(s) == 0:
            return None
        return int(s[0])
    except BaseException, e:
        g_ns2log.exception(e.message)
        return None
    

#----------------------------------------------------------------------
def get_errcode(command):
    """获取错误代码"""
    try:
        s = str(command).split(":")
        if len(s) == 0:
            return None
        return int(s[1])
    except KeyError, e:
        return ERROR_UNKNOW
    except BaseException, e:
        g_ns2log.exception(e.message)
        return None
    
#----------------------------------------------------------------------
def get_data(command):
    """获取数据部分"""
    try:
        s = str(command).split(":")
        if len(s) == 0:
            return None
        return s[2]
    except KeyError, e:
        return None
    except BaseException, e:
        g_ns2log.exception(e.message)
        return None
    
            
                
            
            
        
    
    