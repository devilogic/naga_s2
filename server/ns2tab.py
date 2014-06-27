#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task server data table '

__author__ = 'devilogic'


# 任务类型最大标记
MAX_TASK_TYPE = 16

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
                     "invalid sign",
                     "invalid file server"]

def ns2_error_string(code):
    """从错误代码返回错误字符串"""
    c = code ^ NS2_ERROR_CODE.ERROR_FAILED
    if c >= len(_ns2_error_string):
        return "unknow error code"
    return _ns2_error_string[c]
    
    
########################################################################
class NS2_LOGIN_INFO_TAB:
    """分发服务器注册表"""
    ID = 0                        # 记录索引ID
    NAME = 1                      # 分发服务器名称
    IP = 2                        # 分发服务器IP
    NOTE = 3                      # 分发服务器注释
    TIME = 4                      # 登录时间
    
    # 表名
    login_tab = ('id',
                 'name',
                 'ip',
                 'note',
                 'time')

########################################################################
class NS2_TASK_TAB:
    """任务表"""
    ID = 0                        # 任务ID
    TYPE = 1                      # 任务类型
    STATUS = 2                    # 任务状态
    ERROR = 3                     # 任务出错代码
    COMPLETED = 4                 # 已经经过处理,为了兼容多台分发服务器
    SERVER_NAME = 5               # 哪台服务器获取这个任务
    ROLLBACK_COUNT = 6            # 异常回滚次数
    ARGV = 7                      # 传递给客户端的参数
    # 这里有个简单的例子
    # -l1 $0 -lx $1 -P $2
    # $1表示在ARGV_FILES中第几个sign值
    # 最多可以一次性处理16个文件
    ARGV_FILES = 8                # 所需的文件支持md5队列,使用','号分割
    RESULT = 9                    # 参数返回的结果
    RESULT_FILES = 10             # 参数返回的文件md5队列,使用','号分割
    
    # 表名
    task_tab = ('id', 
                'type',
                'status',
                'error',
                'completed',
                'server_name',
                'rollback_count',
                'argv',
                'argv_files',
                'result',
                'result_count')

########################################################################
class NS2_TASK_STATUS:
    """任务状态"""
    PREPARE = 0                   # 任务正在准备
    READY = 1                     # 任务已经准备完毕,等待获取
    PROCESS = 2                   # 任务正在处理中
    EXCEPTION = 3                 # 任务处理发生异常
    OVER = 4                      # 任务已经处理完毕
    UNKNOW_TYPE = 5               # 未知类型
    
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
    ERROR_SIGN = 0x80000007       # 没有对应的标记算法
    ERROR_FP = 0x80000008         # 没有对应的文件服务器传输协议

########################################################################
class NS2_FILE_INFO:
    """文件存储信息"""
    ID = 0                         # 文件索引
    SIGN = 1                       # 文件的唯一标示
    SIGN_FUNC = 2                  # 文件标示的算法
    HOST = 3                       # 文件服务器的地址
    PORT = 4                       # 服务器链接的端口
    STYPE = 5                      # 服务类型,通常为ftp
    USER = 6                       # 服务器的用户名
    PASSWD = 7                     # 服务器密码
    PATH = 8                       # 服务器路径
    
    # 表名
    file_tab = ('id',
                'sign',
                'sign_func',
                'host',
                'port',
                'stype',
                'user',
                'passwd',
                'path')

        
    
    
        
    
    
        
    
    
