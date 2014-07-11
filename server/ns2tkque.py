#!/usr/bin/env python
# -*- coding: utf-8 -*-

' naga task queue '

__author__ = 'devilogic'

import Queue
import ns2tab
from ns2log import g_ns2log

########################################################################
class Ns2TaskQueue():
    """任务队列"""

    #----------------------------------------------------------------------
    def __init__(self, max_count=20, block=True, time_out=5):
        """Constructor"""
        g_ns2log.info("任务队列分配")
        self.max_count = max_count
        self.time_out = time_out
        self.block = block
        self.retry_time_out = 0
        self.task_queue_dict = {}
        
    #----------------------------------------------------------------------
    def __del__(self):
        """任务队列销毁状况"""
        g_ns2log.info("任务队列销毁")
        
    #----------------------------------------------------------------------
    def set_retry_time_out(time_out=5):
        """设置尝试延迟"""
        self.retry_time_out = time_out
    
    #----------------------------------------------------------------------
    def get_task_queue_dict(self):
        """获取任务队列字典"""
        return self.task_queue_dict
            
    #----------------------------------------------------------------------
    def put_one_task(self, tid, task_list, retry=True):
        """添加一个任务队列到相应的任务类型,一个任务就是一个二元组"""
        
        if tid <= 0:
            raise ValueError("'tid' must be a positive number")
        elif tid > ns2tab.MAX_TASK_TYPE:
            raise ValueError("'tid' must <= %d" % (ns2tab.MAX_TASK_TYPE))
        
        if not isinstance(task_tuple, list):
            raise ValueError("'task_list' must be a list")

        try:
            self.task_queue_dict[tid].put(task_list)
        except KeyError, e:
            k = int(e.message)
            self.task_queue_dict[k] = Queue.Queue(self.max_count)
            curr = self.task_queue_dict[k]
            try:
                curr.put(task_list, self.block, self.time_out)
                return True
            except Queue.Full, e:
                if retry:
                    # 如果队列满了之后,会重新再次尝试一次,如果失败则添加任务失败
                    to = self.retyr_time_out
                    if self.time_out > to:
                        to = self.time_out
                    try:
                        curr.put(task_list, True, to)
                        return True
                    except Queue.Full, e:
                        g_ns2log.info("任务队列已满,重新尝试后无效果")
                        return False
                else:
                    g_ns2log.info("任务队列已满")
                    return False
                
        except BaseException, e:
            g_ns2log.exception(e.message)
            return False

    #----------------------------------------------------------------------
    def get_n_task(self, tid, num, retry=False):
        """获取n个任务"""
        if num <= 0:
            raise ValueError("task number must > 0")
        if num > self.max_count:
            num = self.max_count
        
        if tid <= 0:
            raise ValueError("'tid' must be a positive number")
        elif tid > ns2tab.MAX_TASK_TYPE:
            raise ValueError("'tid' must <= %d" % (ns2tab.MAX_TASK_TYPE))
        
        if not isinstance(task_list, list):
            raise ValueError("'task_list' must be a list")
        
        tasks = []   # 取回的任务
        try:
            curr = self.task_queue_dict[tid]
            for i in range(num):
                try:
                    tasks.append(curr.get(self.block, self.time_out))
                except Queue.Empty, e:
                    # 如果设置了等待
                    if retry:
                        # 如果队列为空之后,会重新再次尝试一次
                        # 只有第一个次强制等待,其余都按照默认处理
                        to = self.retry_time_out
                        if self.time_out > to:
                            to = self.time_out
                        try:
                            tasks.append(curr.get(True, to))
                            for j in range(num - i - 1):
                                tasks.append(curr.get(self.block, self.time_out))
                            return tasks
                        except Queue.Empty, e:
                            return tasks
                    else:
                        return tasks
            return tasks
        except KeyError, e:
            k = int(e.message)
            self.task_queue_dict[k] = Queue.Queue(self.max_count)
            return None
        except BaseException, e:
            g_ns2log.exception(e.message)
            return None
        

if __name__ == '__main__':
    #----------------------------------------------------------------------
    def xxx():
        try:
            i = 7
            i = i / 0
        except BaseException, e:
            print("exp")
            return 1
        finally:
            print("fin")
            
    def test():
        """测试单元"""
        y = xxx()
        print y
        task_list = Ns2TaskQueue()
        task_list.put_one_task(1, (['123'], ['321']))
        print task_list.task_queue_dict[1].get()
        task_list.put_one_task(1, (['122'], ['xxx']))
        task_list.put_one_task(2, (['fdafda'], ['dada']))
        
        v = task_list.get_n_task(1, 10)
        print v[0]
        n = task_list.get_n_task(1, 5, True)
        print n[0]
                        
    test()

            
    
    