#!/usr/bin/python2.6
import sys, socket, string, time, json, os
from httplib import HTTPConnection as HC
from random import choice
from plugins import urban, is_up

class Bot:

    def __init__(self, host, port, nick, ident, owner=None ):
        self.data = self.db_load()
        self.admins = self.data['admins']
        del self.data['admins']
        self.responses = self.data
        del self.data
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.socket = socket.socket()
        self.owner = owner
        if not self.owner in self.admins:
            self.admins.append(owner)
        self.autoreplies = ['^wr', 'Hello there.', 'My ears are ringing..',
                            'WHAT DID YOU SAY?', 'Come at me bro',
                            'Don\'t tase me bro', '...', '^mum %s' % self.owner]
    def connect(self):
        self.socket.connect((self.host, self.port))
        time.sleep(0.2)
        self.socket.send("NICK %s\r\n" % self.nick)
        time.sleep(0.2)
        self.socket.send("USER %s %s bla :%s\r\n" % ( 
        self.ident, self.host, "the bot called %s" % self.nick ))

    def disconnect(self, channel=None):
        print "Quitting..."
        if channel != None:
            self.reply2(channel, choice(['pce', 'l8r', 'bye bye!']))
        self.socket.send("QUIT\r\n")

    def join(self, channel):
        print "==&gt; Joining %s" % channel
        self.socket.send("JOIN %s\r\n" % channel)

    def leave(self, channel, message = 'Bye Bye!'):
        self.reply2(channel, choice(['pce', 'l8r', 'bye bye!']))
        self.socket.send("PART %s :%s\r\n" % (channel, message))

    def pong(self, data):
        self.socket.send("PONG %s\r\n" % data)

    def handleMessage(self, channel, nick, message):
        print "%s on %s: %s" % (nick, channel, message)
        if message[0] == '!':
            print "command %s" % message
            dat = message.split()
            self.handleCommand(channel, nick, dat[0], dat[1:])
        elif message[0] == '.':
            print 'owner cmd %s' % message
            dat = message.split()
            self.ownerCmd(channel, nick, dat[0], dat[1:])
        elif self.nick in message and 'ping' in message.lower():
            print '###PING###'
            self.reply2(channel, 'PONG %s' % nick)
        elif self.nick in message:
            print '%s (PING): %s' % (nick, message)
            self.reply2(channel, choice(self.autoreplies))

    def addResponse(self, command, response):
        self.responses[command] = ' '.join(response)
    
    def remResponse(self, command):
        try:
            del self.responses[command]
        except:
            print 'error'
    def auth_lvl(self, name):
        if name == self.owner:
            return 'owner'
        else:
            if name in self.admins:
                return 'admin'
            else:
                return None
    def ownerCmd(self, channel, nick, command, arguments):
        command = command[1:].lower()
        if command == 'op' and self.auth_lvl(nick[1:]) == 'owner':
            self.socket.send('MODE %s +o %s\r\n' % (channel, arguments[0]))
        elif command == 'dop' and self.auth_lvl(nick[1:]) == 'owner':
            self.socket.send('MODE %s -o %s\r\n' % (channel, arguments[0]))

    def handleCommand(self, channel, nick, command, arguments):
        command = command[1:].lower()
        if command == 'bye':
            if self.auth_lvl(nick[1:]) == 'owner':
                self.disconnect(channel)
                self.db_save()
                exit()
        elif command == 'admin' and self.auth_lvl(nick[1:]) == 'owner':
            self.admins.append(arguments[0])
        elif command == 'dadmin' and self.auth_lvl(nick[1:]) == 'owner':
            try:
                loc = self.admins.index(arguments[0])
                del self.admins[loc]
            except IndexError:
                pass
        elif command == 'isup':
            if is_up.get_code(arguments[0]):
                self.reply(channel,nick, '%s is up! [%i]' % (arguments[0], x))
            else:
                self.reply(channel, nick, '%s appears to be down.' % (arguments[0]))
        elif command == 'join':
            if self.auth_lvl(nick[1:]) =='owner':
                self.join(arguments[0])
        elif command == 'leave':
            if self.auth_lvl(nick[1:]) =='owner':
                self.leave(channel)
        elif command == 'identify':
                self.identify(arguments[0], nick)
        elif command == 'define':
            if self.auth_lvl(nick[1:]) =='admin' or self.auth_lvl(nick[1:]) == 'owner':
                self.addResponse(arguments[0], arguments[1:])
        elif command == 'forget':
            if self.auth_lvl(nick[1:]) == 'owner' or self.auth_lvl(nick[1:]) == 'admin':
                self.remResponse(arguments[0])
        elif command == 'list':
            if self.auth_lvl(nick[1:]) == 'owner' or self.auth_lvl(nick[1:]) == 'admin':
                li = []
                for key in self.responses.keys():
                    li.append(key)
                li.sort()
                li_s = ' '.join(li) 
                self.reply(channel, nick, li_s)
            else: pass
        elif command == 'alist':
            if self.auth_lvl(nick[1:]) == 'owner':
                li = []
                for i in self.admins:
                    li.append(i)
                li = ' '.join(li)
                self.reply(channel, nick, li)
        elif command == 'tell':
            if self.auth_lvl(nick[1:]) == 'admin' or self.auth_lvl(nick[1:]) == 'owner':
                self.reply2(channel, "%s: %s" % (arguments[0], ' '.join(arguments[1:])))
        
        elif command == 'ud':
            data = urban.urban_lookup(arguments)
            self.reply(channel, '', data)

        elif command in self.responses:
            self.reply(channel, nick, self.responses[command])

    def reply(self, channel, nick, message):
        self.socket.send("PRIVMSG %s %s: %s\r\n" % (channel, nick, message))
    
    def reply2(self, channel, message):
        self.socket.send("PRIVMSG %s :%s\r\n" % (channel, message))
    
    def identify(self, pw, n):
        if self.auth_lvl(n[1:]) == 'owner':
            self.reply('NickServ', '', 'IDENTIFY %s' % pw)
    def flush(self):
        print self.socket.recv(4096)

    def mainloop(self):
        readbuffer = ""
        while True:
            data = self.socket.recv(1024)
            if data:
                print data
            readbuffer = readbuffer + data
            temp = string.split(readbuffer, "\n")
            readbuffer=temp.pop()
            for line in temp:
                line = line.rstrip()
                line = line.split()
                # handle possibilities
                if line[0] == 'PING':
                    self.pong(line[1])
                elif line[1] == "PRIVMSG":
                    channel = line[2]
                    nick = line[0].split('!')[0]
                    message = ' '.join(line[3:])[1:]
                    self.handleMessage(channel, nick, message)
                elif line[1] == "NOTICE":
                    nick = line[0].split('!')[0]
                    message = ' '.join(line[3:])[1:]
                    self.handleMessage('', nick, message)

    def db_load(self, fname='cmds.json'):
        try:
            resps = open(fname, 'r')
            data = json.load(resps)
            resps.close()
            return data
        except IOError:
            return {'hi': 'Hi there!', 'admins': []} 

    def db_save(self, fname='cmds.json'):
        with open(fname, 'w') as f:
            data = self.responses
            data['admins'] = self.admins
            json.dump(data, f)
         

if __name__ == "__main__":
    bot = Bot('irc.windfyre.net', 6667, 'gibs0n', 'gibson', 'iAmerikan')
    try:
        bot.connect()
        bot.flush()
        time.sleep(2)
        bot.join('##blackhats')
        bot.mainloop()
        
    except:
        print "interrupt"
        print sys.exc_info()[0]
        bot.disconnect()
        raise
