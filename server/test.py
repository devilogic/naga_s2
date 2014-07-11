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
    yy = {'aa':1, 'b':2, 'c':4}
    for cur in yy.itervalues:
        print cur
    
if __name__ == '__main__':
    main()

