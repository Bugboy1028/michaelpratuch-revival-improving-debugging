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

import os
import string
import time
import traceback
import sys
import sqlite3
import threading
import datetime
import thread

_methods_for_parsing_messages = []
_timers = []
sendMessage = ""

# change the workdir to the plugins directory
workdir = "./plugins/"

# providing database-access
database_lock = threading.Lock()

def dbaccess(con = None):
    if con == None:
        database_lock.acquire()
        connection = sqlite3.connect("./data/database.db", \
                                     detect_types=sqlite3.PARSE_DECLTYPES)
        connection.text_factory = str
        return connection
    else:
        database_lock.release()

def parsing_messageline(line):
    """This parses a line into a message for the plugins
          message = a directory which has following keys:
          message["time"] - System time of the message
          message["sender"] - nickname which send the message
          message["shost"] - the senders host
          message["type"] - type of he message
          message["receiver"] - the receiver of the message
                                #room or user
          message["text"] - the message's text
          message["reply"] - Contains the user of the message (on a
                            query) or the room. Use this to reply
                            to the user who send a message.
          
          The bot can check if somebody is identified vie NickServ via
          a whois-query. then ["type"] is "WHOISRESP" and ["user"] = the
          identified user
          """
    try:
        message = None
        if len(line) >= 2 and line[0] == ":" and "!" in line.split()[0]:
            print line
            message = {}
            message["time"] = datetime.datetime.now()
            message["sender"] = line[1:string.index(line, "!")]
            message["shost"] = string.split(line[string.index(line, "!") + 1:])[0]
            message["type"] = string.split(line)[1]
            if len(line) == 2:
                message["receiver"] = ""
            elif len(line) > 2:
                message["receiver"] = string.split(line)[2]
            if message["type"] == "MODE":
                message["text"] = line[string.index(line, "MODE") + 5:]
            elif message["type"] == "PART":
                message["text"] = ""
            else:
                message["text"] = line[string.index(line, ":", 2) + 1:]
            # let's find how to reply
            if len(message["receiver"]) > 1:
                if message["receiver"][0] == "#":
                    message["reply"] = message["receiver"]
                else:
                    message["reply"] = message["sender"]
            # to be shure that there are not more then one spaces between words
            while "  " in message["text"]:
                message["text"] = string.replace(message["text"], "  ", " ")
            message["text"] = string.strip(message["text"])
            return message
        elif len(string.split(line, " ")) > 1 and \
             string.split(line, " ")[1] == "330" and \
             "is logged in as" in line:
            message = {}
            message["type"] = "WHOISRESP"
            message["user"] = string.split(line, " ")[4]
            return message
    except:
        fout = open("mess_error.txt", "a")
        fout.write("===================\n")
        fout.write("Failed to write: " + line + "\n")
        traceback.print_exc(file=fout)
        fout.close()
        raise
        

def loadPlugins():
    print "Scanning plugins..."
    global _methods_for_parsing_messages
    for (path, dirs, files) in os.walk(workdir):
        if path == workdir:
                for f in files:
                    if f[-3:] == ".py" and f != "__init__.py":
                        print "Found:", f
                        tmodule = __import__(f[:-3])
                        ret_start = tmodule.start()
                        _methods_for_parsing_messages.append(ret_start)
                        try:
                            ret_timers = tmodule.settimer()
                            for ret_timer in ret_timers:
                                ret_timer["lastrun"] = time.time()
                                _timers.append(ret_timer)
                            print "TIMER HINZUGEFUEGT!"
                        except AttributeError, e:
                            if "'module' object has no attribute 'settimer'" \
                               not in str(e):
                                raise

def delegate_message_to_plugins(messageline, sendMessage):
    """ This will be called from the main-function"""
    try:
        message = parsing_messageline(messageline)
        # print message # uncomment to see parsed message
        if message is not None:
            for method in _methods_for_parsing_messages:
                method(message, sendMessage, dbaccess)
    except Exception, e:
        try:
            sys.stderr.write('=== ERROR IN PLUGIN ===\r\n')
            sys.stderr.write(str(e) + "\r\n")
            traceback.print_exc(file=sys.stderr)
            for key, value in message.iteritems():
                svalue = str(value)
                sys.stderr.write(key + " : " + svalue + "\r\n")
            sys.stderr.write('\r\n=== ERROR IN PLUGIN END ===\r\n')
        except Exception, e:
            print e


def proceed_timers():
    global _timers
    while True:
        time.sleep(60)
        for timer in _timers:
            if time.time() - timer["lastrun"] > timer["seconds"]:
                try:
                    function = timer["function"]
                    function(sendMessage, dbaccess)
                    timer["lastrun"] = time.time()
                except Exception, e:
                    sys.stderr.write('\r\n=== ERROR IN TIMER ===\r\n')
                    traceback.print_exc(file=sys.stderr)
                    sys.stderr.write('\r\n=== ERROR IN TIMER END ===\r\n')


thread.start_new_thread(proceed_timers, ())

loadPlugins()
