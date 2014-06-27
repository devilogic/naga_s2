import sys
import socket
import Queue

tasks = Queue.Queue()

def foo(ql):
    ql.put('1234')

#----------------------------------------------------------------------
def foo3(x):
    print x
    
class UIE:
    def __init__(self):
        self.m = []
        pass
    
    def put(self, v):
        self.v = v
        self.m.append(v)
    
    
        

#----------------------------------------------------------------------
def main():
    #name = socket.gethostname()
    #ip = socket.gethostbyname(socket.gethostname())
    #print '%s-%s\n' % (name,ip)
    foo(tasks)
    #xxx = [['1','2','3'], '1', '2', ['33']]
    #yyy = [['4','5','6'], '1', '2', ['xx']]
    #xxx.append(yyy)
    #print xxx
    pp = UIE()
    pp.put(1928)
    pp.put(1212)
    pp.put(1212)
    pp.put(1212)
    print pp.m
    oo = [1,2,3,4]
    foo3(oo)
    v = tasks.get()
    #print v
    io = Queue.Queue()
    io.put(1)
    io1 = Queue.Queue()
    io1.put(2)
    x = {1:io, 3:io1}
    try:
        print x[1].get()
        print x[3].get()
        print x[2].get()
        
        x[2].put(3)
    except KeyError, e:
        x[e] = Queue.Queue()
        x[e].put(3)
        print x[e].get()
        try:
            i = 5 / 0
        except BaseException, e:
            print e
    
if __name__ == '__main__':
    main()

