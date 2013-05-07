#!/usr/bin/python2 

class MsgStack(object):

    def __init__(self):
        self._stack = []
    
    def push(self, msg):
        self._stack.insert(0, msg) # !lifo
    
    def pop(self):
        return self._stack.pop()

    def isEmpty(self):
        return self._stack == []


# test
if __name__ == '__main__':
    ms = MsgStack()

    for s in "Hi there, what's your name?".split(' '):
        ms.push(s)

    while not ms.isEmpty():
        print ms.pop()
