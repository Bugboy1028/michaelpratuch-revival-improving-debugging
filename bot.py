#!/usr/bin/env python

"""
Isidore - Python IRC Bot

Copyright (C) 2010 Sebastian Meyer (s.meyer@drachenjaeger.eu)

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this 
program; if not, see <http://www.gnu.org/licenses/>
"""

import socket
import thread
import string
import time
import sys
import threading
import traceback
import datetime

sys.path.append("./plugins")

# default values
# TODO: command line parameters
network = 'irc.freenode.net'
port = 8001
nick = "ircbottest"
room = "ircbottest"
timeout = 160
pingtime = 100
lastping = 0

irc = None
orignick = nick

#queue for data to send
__data_to_send = []
#lock for the queue
send_queue_lock = threading.Lock()
#lock for the sending socket
send_socket_lock = threading.Lock()
#thread event to stop the sending-thread on empty queue
send_event = threading.Event()


def login():
    """Sending Login-Data to the IRC-Server"""
    send("NICK " + nick)
    send("USER ircbottest host server : ircbot")
    

def send(data, highPriority=False):
    """Sending data - Critical section"""
    send_queue_lock.acquire()
    if highPriority == False:
        __data_to_send.append(data)
    else:
        __data_to_send.insert(0, data)
    send_event.set()
    send_queue_lock.release()
    

def send_data_to_socket():
    try:
        while True:
            send_queue_lock.acquire()
            if len(__data_to_send) > 0:
                tosend = __data_to_send[0]
                del __data_to_send[0]
                send_queue_lock.release()
                send_socket_lock.acquire()
                irc.send(tosend + "\r\n")
                send_socket_lock.release()
                time.sleep(0.7)
            else:
                send_queue_lock.release()
                send_event.clear()
            send_event.wait()
    except Exception, e:
        send_queue_lock.release()
        print e
        traceback.print_exc(file=sys.stderr)


def sendMessage(text, receiver, msgtype="PRIVMSG"):    
    """ Note: SYSTEM MESSAGES must been fully written in text"""
    global send_message_lock
    send_message_lock = threading.Lock()
    send_message_lock.acquire()
    if msgtype == "SYSTEM":
        send(text, highPriority=True)
    else:
        send(msgtype + " " + receiver + " :" + text)
    send_message_lock.release()
        

def parseIncomingData(linein):
    """Parsing incoming data, basic operations."""
    global nick
    line = string.strip(linein)
    # print "IN:", line
    if line[0:4] == "PING":
        #Must response to the PING afap
        #using the socket dirctly, so i need to lock it
        global lastping
        lastping = time.time()
        send_socket_lock.acquire()
        irc.send("PONG" + line[4:]+"\r\n")
        send_socket_lock.release()
    elif "Found your hostname" in line:
        login()
    elif "Nickname is already in use." in line:
        nick = nick + "_"
        login()
    elif "Message of the Day" in line:
        send ("JOIN #" + room)
    else:
        thread.start_new_thread(p.delegate_message_to_plugins, (linein, sendMessage,))

    
def readData():
    while True:
        global irc
        global nick
        nick = orignick
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        irc.settimeout(timeout)
        irc.connect((network, port))
        while True:
            try:
                intext = irc.recv(1024)
                for line in intext.split("\r\n"):
                    parseIncomingData(line)
            except socket.timeout, msg:
                print "Socket error:", msg
                print "going to reconnect..."
                parseIncomingData(":botlog!bot@localhost LOG LOG :Disconnect")
                irc.close()
                break


def pingserver():
    while True:
        try:
            global irc
            time.sleep(pingtime)
            send_socket_lock.acquire()
            irc.send("PING myself\r\n")
            send_socket_lock.release()
        except Exception, e:
            sys.stderr.write(datetime.datetime.now() + '==> Error while pinging the server (just an info)\r\n')
            sys.stderr.write(str(e) + "\r\n")
            traceback.print_exc(file=sys.stderr)
        


if __name__ == "__main__":
    global p
    import plugins
    p = plugins
    p.sendMessage = sendMessage
    thread.start_new_thread(send_data_to_socket, ())
    thread.start_new_thread(pingserver, ())
    readData()

