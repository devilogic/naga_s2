#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task server data table '

__author__ = 'devilogic'


# 任务类型最大标记
MAX_TASK_TYPE = 16
    
########################################################################
class NS2_LOGIN_INFO_TAB:
    """分发服务器注册表"""
    ID = 0                        # 记录索引ID
    NAME = 1                      # 分发服务器名称
    IP = 2                        # 分发服务器IP
    NOTE = 3                      # 分发服务器注释
    TIME = 4                      # 登录时间
    
    table_name = 'login_info'
    # 表名
    login_tab = ('id',
                 'name',
                 'ip',
                 'note',
                 'time')

########################################################################
class NS2_TASK_TAB:
    """任务表"""
    TASK_ID = 0                   # 任务ID
    TYPE = 1                      # 任务类型
    STATUS = 2                    # 任务状态
    CLIENT_NAME = 3               # 哪台客户端处理完这个任务"IP:PORT"
    ROLLBACK_COUNT = 4            # 异常回滚次数
    ARGV = 5                      # 传递给客户端的参数
    # 这里有个简单的例子
    # -l1 $0 -lx $1 -P $2
    # $1表示在ARGV_FILES中第几个sign值
    # 最多可以一次性处理16个文件
    ARGV_FILES = 6                # 所需的文件支持md5队列,使用','号分割
    RESULT = 7                    # 参数返回的结果
    RESULT_FILES = 8              # 参数返回的文件md5队列,使用','号分割
    PROCESS_BAR = 9               # 进度条
    ERROR_CODE = 10               # 任务出错代码
    
    table_name = 'tab_task'    
    
    # 表名
    task_tab = ('task_id', 
                'type',
                'status',
                'client_name',
                'rollback_count',
                'argv',
                'argv_files',
                'result',
                'result_files',
                'process_bar',
                'error_code')

########################################################################
class NS2_TASK_STATUS:
    """任务状态"""
    PREPARE = 0                   # 任务正在准备
    READY = 1                     # 任务已经准备完毕,等待获取
    CACHE = 2                     # 任务已经被服务器缓存,但是还没有获取
    PROCESS = 3                   # 任务正在被客户端处理中
    EXCEPTION = 4                 # 任务处理发生异常
    OVER = 5                      # 任务已经处理完毕
    UNKNOW_TYPE = 6               # 未知类型
    
g_ns2_status_process = [0, 30, 50, 70, 100, 100, 0]


########################################################################
class NS2_FILE_INFO:
    """文件存储信息"""
    FILE_ID = 0                    # 文件索引
    SIGN = 1                       # 文件的唯一标示
    HOST = 2                       # 文件服务器的地址
    PORT = 3                       # 服务器链接的端口
    USER = 4                       # 服务器的用户名
    PASSWD = 5                     # 服务器密码
    PATH = 6                       # 服务器路径
    
    table_name = 'tab_file'
    
    # 表名
    file_tab = ('file_id',
                'sign',
                'host',
                'port',
                'user',
                'passwd',
                'path')

    
    
        
    
    
        
    
    
