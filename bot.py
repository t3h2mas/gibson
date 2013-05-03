#!/usr/bin/python2

import socket
import time

class Gibson(object):
    
    def __init__(self): # user stuff here
        pass

    def connect(self):
        self.s = socket.socket()
        self.s.connect(('irc.windfyre.net', 6667))
        self.s.send('NICK gibson\r\n')
        self.s.send('USER bob 0 * :vato\r\n')
        #self.s.send('MODE gibson +B')
        # this goes in self.loop or something
        #self.s.send('JOIN :blackhats')
        while True:
            line = self.s.recv(500)
            if not line: break # ?
            print line
            line = line.rstrip()
            line = line.split()
            if line[0] == "PING":
                print 'PONG ' + line[1]
                self.s.send('PONG ' + line[1] + '\r\n')
            if str(376) in line:
                time.sleep(2)
                self.s.send("JOIN #blackhats\r\n")
        self.s.close()
            
