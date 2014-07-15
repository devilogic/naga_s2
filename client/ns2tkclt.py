#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task handle client '

__author__ = 'devilogic'

import os
import sys
import time
import random
import ConfigParser

from multiprocessing import Process
from multiprocessing import Pool
from twisted.internet import reactor, protocol

DEF_CONFIG_DIR = './config/'
DEF_WORKSPACE_DIR = './workspace/'
DEF_TOOL_DIR = './tool/'

class Ns2TaskSubClient(protocol.ClientFactory):
    def __init__(self, name, pid, config_path, workspace_dir, tool_path):
        try:
            self.name = name
            self.pid = pid
            self.workspace_dir = workspace_dir
            self.tool_path = tool_path
        
            config = ConfigParser.ConfigParser()
            config.read(config_path)
        
            self.ip = config.get("SERVER", "ip")
            self.port = config.getint("SERVER", "port")
            self.task_type = config.getint("CLIENT", "type")
            self.tool_type = config.get("CLIENT", "tool_type")
            self.tool_run = { 'exe' : run_exe, 'script' : run_script }
            
            # 运行
            self.run()
            
        except BaseException, e:
            print e.message
            pass
        finally:
            pass
        
    def run_exe(self):
        #Process()
        pass
    
    def run_script(self):
        pass
    
    def __def__(self):
        pass
    
    def run(self):
        try:
            # 创建工作目录
            sub_workspace_dir = self.workspace_dir + str(self.pid) + "/"
            os.mkdir(sub_workspace_dir)
            
        except BaseException, e:
            pass
        finally:
            # 删除自身工作目录
            os.rmdir(sub_workspace_dir)
    

def sub_proc_run(name, config_path, workspace_dir, tool_path):
    pid = os.getpid()
    print 'Run task %s (%s)...' % (name, pid)
    start = time.time()

    config = ConfigParser.ConfigParser()
    config.read(config_path)

    self.ip = config.get("SERVER", "ip")
    self.port = config.getint("SERVER", "port")

    reactor.connectTCP(self.ip, self.port, Ns2TaskSubClient(name, config_path, workspace_dir, tool_path))
    reactor.run()

    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))          


class Ns2TaskClient:
    """任务处理客户端"""
    def __init__(self):
        self.proc_pool = None
    
    def __def__(self):
        wait_for_all_sub()
    
    def wait_for_all_sub(self):
        self.proc_pool.close()
        self.proc_pool.join()
        
    def run(self):
        """运行"""
        try:
            # 读起配置文件
            config = ConfigParser.ConfigParser()
            config_file_path = DEF_CONFIG_DIR + 'client.ini'
            if os.path.isfile(config_file_path) == False:
                print "配置文件 '%s' 不存在" % config_file_path
                return False
            
            config.read(config_file_path)
            self.process = config.getint("CONFIG", "process")
            self.tool_name = config.get("CLIENT", "tool")
            tool_path = DEF_TOOL_DIR + self.tool_name
            
            # 根据配置文件开辟子进程
            if self.process == 0:
                self.process = 1
            
            self.proc_pool = Pool(self.process)
            
            for i in range(self.process):
                self.proc_pool.apply_async(sub_proc_run, args=(i,config_file_path,DEF_WORKSPACE_DIR,tool_path))
            
            # 父进程等待子进程全部执行完毕
            self.wait_for_all_sub()
            
            # 父进程清理子进程的工作目录
            # 进入下一轮
            return True
        except BaseException, e:
            return False
        finally:
            pass
    
    
if __name__=='__main__':
    def main():
        client = Ns2TaskClient()
        client.run()
    
    main()