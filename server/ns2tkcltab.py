#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga server 2 task - client table '

__author__ = 'devilogic'

import threading

from ns2log import g_ns2log

########################################################################
class Ns2TaskClientTable:
    """任务类型-客户端对应表"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.clients = {}
        self.client_lock = threading.Lock()
        
    #----------------------------------------------------------------------
    def __len__(self):
        """取长度"""    
        return len(self.clients)
    
    #----------------------------------------------------------------------
    def get_task_id_list(self):
        """获取任务类型表,这个本来用迭代器实现比较好，没时间了所以这样用了"""
        tid_list = []
        try:
            self.client_lock.acquire()
            for i in self.clients:
                tid_list.append(i)
            return tid_list
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None
        finally:
            self.client_lock.release()
    
    #----------------------------------------------------------------------
    def new_client(self, tid, client_address, client_sign):
        """新的客户端"""
        try:
            self.client_lock.acquire()
            self.clients[tid][client_address].append(client_sign)
        except BaseException, e:
            g_ns2log.exception(e.message)
        finally:
            self.client_lock.release()
            
    #----------------------------------------------------------------------
    def del_client_by_hostport(self, hostport):
        """删除客户端"""
        try:
            self.client_lock.acquire()
            
            if len(self.clients) == 0:
                return
                
            # 遍历所有任务类型
            for task_type in self.clients:
                client_array = self.clients[task_type]
                # 如果为空则整只删除这个任务类型
                if len(client_array):
                    dict(self.clients).pop(task_type)
                
                # 遍历所有再当前任务类型下的 客户端列表
                for client_address in client_array:
                    if client_address == hostport:
                        dict(client_array).pop(client_address)
        except BaseException, e:
            g_ns2log.exception(e.message)
        finally:
            self.client_lock.release()
            
    #----------------------------------------------------------------------
    def find_client_by_hostport(self, hostport):
        """通过ip＋端口寻找客户端"""
        try:
            self.client_lock.acquire()
            
            if len(self.clients) == 0:
                return False
                
            # 遍历所有任务类型
            for task_type in self.clients:
                client_array = self.clients[task_type]
                # 如果为空则整只删除这个任务类型
                if len(client_array):
                    return False
                
                # 遍历所有再当前任务类型下的 客户端列表
                for client_address in client_array:
                    if client_address == hostport:
                        return True
            return False  
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False
        finally:
            self.client_lock.release()
            
    #----------------------------------------------------------------------
    def find_task_id(self, task_id):
        """寻找任务类型"""
        try:
            if len(self.clients) == 0:
                return None
            
            for t in self.clients:
                if t == task_id:
                    if len(self.clients[t]) == 0:
                        return None
                    else:
                        return self.clients[t]
            return None
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None
        finally:
            self.client_lock.release()
    
 
g_tkcltab = Ns2TaskClientTable()  
    
     
        
        
    
    