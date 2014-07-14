# -*- coding: utf-8 -*-

' naga task server protocol '

__author__ = 'devilogic'


from ns2ptl import *
from ns2log import g_ns2log

########################################################################
class NS2_CLIENT_COMMAND:
    """客户端向服务器发送的命令"""
    CLIENT_NONE = 0
    CLIENT_LOGIN = 1                  # 数据为客户端信息
    CLIENT_REQUEST_TASK = 2           # 数据为具体要获取的任务数量
    CLIENT_TASK_COMPLETED_1 = 3       # 无数据
    CLIENT_TASK_COMPLETED_2 = 4       # 按照具体情况，如果存在即存放入数据库的result字段
    CLIENT_COMMAND_MAX = 4

########################################################################
class NS2_SERVER_COMMAND:
    """服务器向客户端发送的命令"""
    SERVER_TASK_READY = 1             # 数据区域就是任务列表
    SERVER_TASK_GO_NEXT = 2           # 无数据
    SERVER_TASK_IGNORE = 3            # 无数据
    SERVER_COMMAND_MAX = 3
    
########################################################################
class NS2_ERROR_CODE:
    """任务处理出错代码"""
    ERROR_SUCCESS = 0             # 成功
    ERROR_FAILED = 0x80000000     # 失败
    ERROR_MISS_FILE = 0x80000001  # 命令行所需要的文件在列表中不足
    ERROR_CONN_FS = 0x80000002    # 链接文件服务器失败
    ERROR_UP_FILE = 0x80000003    # 上传文件失败
    ERROR_DL_FILE = 0x80000004    # 下载文件失败
    ERROR_EXEC = 0x80000005       # 客户端业务失败
    ERROR_ARGV = 0x80000006       # 客户端参数错误
    ERROR_MISS_TOOL = 0x80000007  # 丢失tool工具
    ERROR_UNKNOW = 0x80000008     # 未知错误
    
#----------------------------------------------------------------------
def ns2_success(code):
    """判断是否执行成功"""
    if code & NS2_ERROR_CODE.ERROR_FAILED:
        return False
    return True
    
#----------------------------------------------------------------------
_ns2_error_string = ["failed",
                     "miss file", 
                     "connect file server failed",
                     "upload file failed",
                     "download file failed",
                     "client exec failed",
                     "invalid arguments",
                     "miss tool"]
    
def ns2_error_string(code):
    """从错误代码返回错误字符串"""
    c = code ^ NS2_ERROR_CODE.ERROR_FAILED
    if c >= len(_ns2_error_string):
        return "unknow error code"
    return _ns2_error_string[c]

    
#----------------------------------------------------------------------
import re
def check_client_command(line):
    """检查一条客户端发来的命令是否合法"""
    try:
        # xxx:yyy:zzz:000
        match = re.match(r'.*:.*:.*:.*', line)
        if match:
            return True
        else:
            return False
    except BaseException, e:
        g_ns2log.exception(e.message)
        return False
    
#----------------------------------------------------------------------
def make_command(cmd, errcode, data):
    """合成一个命令字符串"""
    command = "%d:%d:%s\r\n" % (cmd, errcode, data)
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
def get_task_id(command):
    """获取任务id"""
    try:
        s = str(command).split(":")
        if len(s) == 0:
            return None
        return int(s[1])
    except BaseException, e:
        g_ns2log.exception(e.message)
        return None   
    
#----------------------------------------------------------------------
def get_task_type(command):
    """获取任务id"""
    try:
        s = str(command).split(":")
        if len(s) == 0:
            return None
        return int(s[1])
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
        return int(s[2])
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
        return s[3]
    except KeyError, e:
        return None
    except BaseException, e:
        g_ns2log.exception(e.message)
        return None
    
            
                
            
            
        
    
    