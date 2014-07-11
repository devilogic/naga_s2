#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga server log module '

__author__ = 'devilogic'

import sys
import logging
import logging.config
import threading

DEF_LOG_CONF = "./ns2log.conf"
DEF_LOGGER = "debugLog"
DEF_LOG_CONF_SERVER_PORT = 65534
DEF_LOG_TIME_OUT = 5


########################################################################
class Ns2Log:
    """naga server log"""

    #----------------------------------------------------------------------
    def __init__(self, filepath=DEF_LOG_CONF, log=DEF_LOGGER, 
                 log_server_enable=False, log_server_port=DEF_LOG_CONF_SERVER_PORT,
                 log_server_time_out=DEF_LOG_TIME_OUT):
        """Constructor"""
        try:
            logging.config.fileConfig(filepath)
            self.logger = logging.getLogger(log)
            self.log_server_time_out = log_server_time_out
            self.log_server_port = log_server_port
            self.log_server_enable = log_server_enable

            # 设置日志配置服务器
            if self.log_server_enable == True:
                self.make_server(self.log_server_port)
        except:
            print 'log start failed'

    #----------------------------------------------------------------------
    def __del__(self):
        """析构函数"""
        if self.log_server_enable:
            logging.config.stopListening()
            self.log_server.join(self.log_server_time_out)
            self.log_server_enable = False
    
    #----------------------------------------------------------------------
    def make_server(self, bindport=DEF_LOG_CONF_SERVER_PORT):
        """生成一个日志服务器,允许任意修改配置"""
        try:
            self.log_server = logging.config.listen(bindport)
            self.log_server.start()
            self.enable_log_server = True
        except:
            self.enable_log_server = False

    #----------------------------------------------------------------------
    def debug(self, message):
        """调试信息"""
        self.logger.debug(message)
        
    #----------------------------------------------------------------------
    def info(self, message):
        """一般信息"""
        self.logger.info(message)
        
    #----------------------------------------------------------------------
    def warn(self, message):
        """警告信息"""
        self.logger.warn(message)
        
    #----------------------------------------------------------------------
    def error(self, message):
        """错误信息"""
        self.logger.error(message)
        
    #----------------------------------------------------------------------
    def critical(self, message):
        """严重错误"""
        self.logger.critical(message)
    
    #----------------------------------------------------------------------
    def exception(self, message):
        """异常记录"""
        self.logger.exception(message)
        
    #----------------------------------------------------------------------
    def set_log_level(self, level):
        """设置日志记录级别"""
        self.logger.setLevel(level)
        
    #----------------------------------------------------------------------
    def restart(self, filepath=DEF_LOG_CONF, log=DEF_LOGGER, 
                 log_server_enable=False, log_server_port=DEF_LOG_CONF_SERVER_PORT,
                 log_server_time_out=DEF_LOG_TIME_OUT):
        """重新启动日志记录"""
        try:
            logging.config.fileConfig(filepath)
            self.logger = logging.getLogger(log)
            self.log_server_time_out = log_server_time_out
            self.log_server_port = log_server_port
            self.log_server_enable = log_server_enable

            # 设置日志配置服务器
            if self.log_server_enable == True:
                self.make_server(self.log_server_port)
        except:
            print 'log restart failed'
        


################################################################################
# 全局变量
################################################################################
g_ns2log = Ns2Log(DEF_LOG_CONF, 'infoLog', True)        
        
        
import time
if __name__ == "__main__":
    def test():
        """测试单元"""        
        log = Ns2Log(DEF_LOG_CONF, DEF_LOGGER, True)
        log.debug("hello world")
        log.info("hello world")
        log.error("hello world")
        
    test()
    