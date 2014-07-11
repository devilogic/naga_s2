#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga server 2 '

__author__ = 'devilogic'

from ns2tksrv import *

# 任务分发服务器类
g_tasksrv = Ns2TaskServer()

def main():
    g_tasksrv.Start()
   

if __name__ == '__main__':
    main()
