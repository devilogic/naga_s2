#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga server log module '

__author__ = 'devilogic'

import logging
import logging.config

DEF_LOG_CONF = "./ns2_log.conf"
DEF_LOGGER = "default"

########################################################################
class Ns2Log:
    """naga server log"""

    #----------------------------------------------------------------------
    def __init__(self, filepath=DEF_LOG_CONF, log=DEF_LOGGER):
        """Constructor"""
        logging.config.fileConfig(filepath)
        self.logger = logging.getLogger(log)
        
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
    def set_log_level(self, level):
        """设置日志记录级别"""
        self.logger.setLevel(level)
        
    #----------------------------------------------------------------------
    def restart(self, filepath=DEF_LOG_CONF, log=DEF_LOGGER):
        """重新启动"""
        logging.config.fileConfig(filepath)
        self.logger = logging.getLogger(log)
        
        
if __name__ == "main":
    #----------------------------------------------------------------------
    def test():
        """测试单元"""
        pass
        
    test()
    