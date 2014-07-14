#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task master server '

__author__ = 'devilogic'

import sys
import time

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor

import ns2tab
from ns2db import *
from ns2ptl import *
from ns2log import g_ns2log
from ns2tkcltab import g_tkcltab
from ns2tksrv import *

global g_ns2db

########################################################################
class Ns2Protocol(LineOnlyReceiver):
    """ns2协议"""
    #----------------------------------------------------------------------
    def __init__(self, factory):
        """初始化"""
        self.factory = factory

    #----------------------------------------------------------------------
    def connectionLost(self, reason):
        """链接丢失时调用,从任务类型-客户端列表中删除对应的客户端"""
        client_address = "%s:%d" % (self.transport.client[0], self.transport.client[1])
        self.factory.del_client(client_address)

    #----------------------------------------------------------------------
    def connectionMade(self):
        """链接时调用"""
        client = self.transport.getPeer()
        g_ns2log.info("有新的客户端链接 : %s" % client)

    #----------------------------------------------------------------------
    def client_none(self, error_code, line):
        """无用"""
        try:
            g_ns2log.error("无效的客户端命令")
        except BaseException, e:
            g_ns2log.exception(e.message)


    #----------------------------------------------------------------------
    def client_login(self, error_code, task_type, data):
        """客户端登录时调用"""
        try:
            pid = int(data)
            self.factory.add_client(task_type, pid)
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
            
    
    #----------------------------------------------------------------------
    def client_request_task(self, error_code, task_type, data):
        """客户端请求任务"""
        try:
            # 这里直接采用了客户端向服务端发送任务类型，这样快些
            # 否则必须反查任务类型 - 客户端对应表
            
            task_num = int(data)     # 获取任务数量
            
            # 这里应该做task_num的判断
            
            # 从任务队列重获取
            client_name = "%s:%d" % (self.transport.client[0], self.transport.client[1])
            tasks = g_ns2db.get_task_string(task_type, task_num, client_name)
            
            # 发送给客户端
            make_command(NS2_SERVER_COMMAND.SERVER_TASK_READY, 
                         NS2_ERROR_CODE.ERROR_SUCCESS, tasks)
            self.transport.write(tasks)
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
    
    #----------------------------------------------------------------------
    def client_handle_task(self, error_code, task_id, data):
        """客户端完成第一阶段处理"""
        cmd = 0
        # 任务第一次被处理
        if ns2_success(error_code) == False:
            # 检查回滚数量,如果不等于0则重置任务
            cmd = NS2_SERVER_COMMAND.SERVER_TASK_IGNORE
            if len(task_id) == 0:
                raise ValueError("task_id is empty")
            
            task_id = int(task_id)
            rollback = g_ns2db.get_task_rollback(task_id)
            
            # 进行回滚
            if rollback > 0:
                g_ns2db.dec_task_rollback_c(task_id)
                # 标记任务为准备
                g_ns2db.update_task_status_processbar(task_id, NS2_TASK_STATUS.READY)
            else:
                # 标记任务为异常,这里可以做进一步的容错处理
                g_ns2db.update_task_status_processbar(task_id, NS2_TASK_STATUS.EXCEPTION)
                            
        else:
            # 向客户端发送进入下一阶段,这里其实可以增加一个进度条
            cmd = NS2_SERVER_COMMAND.SERVER_TASK_GO_NEXT
            
        # 更新错误代码
        g_ns2db.update_task_errcode(task_id, error_code)
          
        return cmd
        
    #----------------------------------------------------------------------
    def client_task_completed_1(self, error_code, task_id, data):
        """客户端完成第一阶段,数据部分为结果,按照需要设置"""
        try:
            # 查询是上一次处理的状态,如果是成功,则丢弃任务。
            # 否则继续处理
            status = g_ns2db.get_task_status(task_id)
            if status != NS2_TASK_STATUS.OVER:                    
                cmd = self.client_handle_task(error_code, task_id, data)
            else:
                # 上一次成功则ignore掉它
                cmd = NS2_SERVER_COMMAND.SERVER_TASK_IGNORE
            
            # 发送给客户端
            result = data
            if len(result):
                # 更新结果到数据库
                g_ns2db.update_task_result(task_id, result)
            
            tasks = make_command(cmd, NS2_ERROR_CODE.ERROR_SUCCESS, "")
            self.transport.write(tasks)
            
        except BaseException, e:
            g_ns2log.exception(e.message)  
            return False

    #----------------------------------------------------------------------
    def client_task_completed_2(self, error_code, task_id, data):
        """客户端完成第二阶段,数据部分为文件列表"""
        try:
            # 查询客户端返回是否上传成功
            if ns2_success(error_code) == False:
                self.client_handle_task(task_id, error_code, task_id, data)
            else:
                result_files = data
                file_signs = []
                r_info = []
                if len(result_files):
                    result_files_list = str(result_files).split(",")
                    # 遍历所有任务文件
                    for one_result_file in result_files_list:
                        # 取出6个字段
                        r = str(one_result_file).split('|')
                        if len(r) != 6:
                            # 出错,这里先不做处理
                            g_ns2log.error("客户端发来的结果文件缺少字段")
                            return False
                        
                        # 这里应该向服务器查询，当前文件是否已经上传
                        # 这里先这样做，以后全部跑通再慢慢修改
                        
                        file_signs.append(r[0])
                        r_info.append(r)

                    # 更新结果到数据库                    
                    g_ns2db.update_task_result_files(task_id, file_signs)
                    # 将文件结果插入到文件表中
                    g_ns2db.insert_files_info(r)
                else:
                    # 结果列表为空
                    pass
                
                # 更新状态为完成
                g_ns2db.update_task_status_processbar(task_id, NS2_TASK_STATUS.OVER)
                
            # 设置任务完成
            g_ns2db.set_task_completed(task_id, 1)
            return True
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def lineReceived(self, line):
        """接收到一行数据时调用,以'\r\n'结尾的行
        [命令]:[任务id]:[出错代码]:[返回的一些结果,根据命令不同而不同]
        命令与出错代码必须存在,而数据不一定存在。
        [命令]
        客户端注册                  1
        客户端请求任务               2
        客户端完成任务第一阶段        3
        客户端完成任务第二阶段        4
        """
        try:
            g_ns2log.info("接收到数据 : %s" % line)
            # 判断是否符合协议规则,不符合直接返回
            if check_client_command(line) == False:
                return
            
            # 获取命令
            command = get_command(line)
            if command == None:
                return
            # 获取task_x
            task_x = get_task_id(line)
            if task_x == None:
                return
            
            # 获取出错代码
            errcode = get_errcode(line)
            if errcode == None:
                return
            
            # 获取数据
            data = get_data(line)
            if data == None:
                return
            
            # 如果客户端返回出错
            if ns2_success(errcode) == False:
                g_ns2log.error("接收到错误代码 : (%s)%x" % ns2tab.ns2_error_string(errcode), errcode)

            # 检验命令合法性
            if command < 0:
                raise ValueError("client command must be > 0")
            elif command > NS2_CLIENT_COMMAND.CLIENT_COMMAND_MAX:
                raise ValueError("client command must be < %d" % NS2_CLIENT_COMMAND.CLIENT_COMMAND_MAX)

            # 进行处理
            handler = self.client_handler[command]
            ret = handler(errcode, task_x, data)
            
            # 处理出错
            if ret == False:
                return
                
        except BaseException, e:
            g_ns2log.exception(e.message)
            g_ns2log.info("娜迦协议处理模块接收数据出错")


########################################################################
class Ns2Master(Factory):
    """用于响应客户端发来的包"""
    #----------------------------------------------------------------------
    def __init__(self):
        """初始化"""
        g_ns2log.info("娜迦工厂模块启动")

    #----------------------------------------------------------------------
    def __del__(self):
        """析构函数"""
        pass

    #----------------------------------------------------------------------
    def buildProtocol(self, addr):
        """建立协议"""
        return Ns2Protocol(self)

    #----------------------------------------------------------------------
    def add_client(self, task_type, pid):
        """增加客户端"""
        try:
            client_address = "%s:%d" % (self.transport.client[0], self.transport.client[1])
            
            # 新的客户端
            g_tkcltab.new_client(task_type, client_address, pid)
            
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None

    #----------------------------------------------------------------------
    def del_client(self, client_address):
        """当客户端丢失时调用，用于删除客户端,client_address为 ip:port"""
        if len(g_tkcltab) == 0:
            return False
        
        try:
            g_tkcltab.del_client_by_hostport(client_address)
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False


if __name__ == '__main__':
    #----------------------------------------------------------------------
    def test():
        pass

    test()