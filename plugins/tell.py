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

import string
import datetime
import time
import threading

awaited_users_lock = threading.Lock()

awaited_users = {}


def start():
    print "Module for personal messages..."
    return tellparser

def tellparser(message, sendMessage, dbaccess):
    # first looking for a whois answer
    if message["type"] == "WHOISRESP":
        print "WHOIS KOMMT REIN!"
        incomingWhois(message, sendMessage, dbaccess)
    elif message["type"] == "NICK":
        checkForMessages(message["text"], sendMessage, dbaccess)
    elif message["type"] == "JOIN":
        checkForMessages(message["sender"], sendMessage, dbaccess)
    elif message["type"] == "PRIVMSG":
        command = string.lower(string.split(message["text"], " ")[0])
        if len(string.split(message["text"], " ")) == 1 \
           and command == "!help":
            sendMessage("!TELL <Nickname> <Message> : Leave a (private) " + \
                       "Message for a User.", message["sender"])
            sendMessage("!READ : read private Messages (try !HELP READ)", \
                        message["sender"])
        elif len(string.split(message["text"], " ")) == 2 \
           and command == "!help" \
           and string.lower(string.split(message["text"], " ")[1]) == "read":
            sendMessage("!READ [x] sends max. 10 private messages, starting " + \
                        "with message x via query to you", message["sender"])
        elif command in ("!tell", "!read"):
            if message["receiver"][0] == "#":
                response = message["receiver"]
            else:
                response = message["sender"]
            if command == "!tell":
                if len(string.split(message["text"], " ")) < 3:
                    sendMessage(message["sender"] + ": Wrong Syntax, " + \
                      "please use: !TELL <Nickname> <Message>", response)
                else:
                    tell(message, sendMessage, dbaccess, response)
            elif command == "!read":
                read(message, sendMessage, dbaccess, response)


def checkForMessages(receiver, sendMessage, dbaccess):
    con = dbaccess()
    try:
        cursor = con.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM tellmsg " + \
                               "WHERE receiver = ? AND read = 'False'", \
                               (receiver,)).fetchall()[0][0]
        if count > 0:
            sendMessage("Hi " + receiver + ". I have some new mesasges " + \
                        "for you. Please query me with !READ to read them.",\
                        receiver)
        con.close()
        dbaccess("release")
    except Exception, e:
        if "no such table" in str(e):
            createTellTable(cursor)
            dbaccess("release")
            checkForMessages(receiver, sendMessage, dbaccess)
        else:
            dbaccess("release")
            raise


def incomingWhois(message, sendMessage, dbaccess):
    message["user"] = string.lower(message["user"])
    send = False
    awaited_users_lock.acquire()
    if message["user"] in awaited_users \
       and awaited_users[message["user"]]["time"] - time.time() < 20:
        startmess = awaited_users[message["user"]]["startmess"]
        del awaited_users[message["user"]]
        send = True
    awaited_users_lock.release()
    if send == True:
        try:
            con = dbaccess()
            cursor = con.cursor()
            count = cursor.execute("SELECT COUNT(*) FROM tellmsg " + \
                                   "WHERE receiver = ?", \
                                   (message["user"],)).fetchall()[0][0]
            if count == 0:
                sendMessage("Sorry, there are no messages saved for you.",\
                            message["user"])
            else:
                sendMessage("I saved " + str(count) + " messages for you. " + \
                            "I show you 10, starting with message " + \
                            str(startmess), message["user"])
                mails = cursor.execute("SELECT sender, date, text, read " + \
                                       "FROM tellmsg WHERE receiver = ? " + \
                                       "ORDER BY date DESC " + \
                                       "LIMIT "+ str(startmess) + ", 10", \
                                       (message["user"],)).fetchall()
                for mail in mails:
                    sender = mail[0]
                    date = str(mail[1])[:16]
                    text = mail[2]
                    read = mail[3]
                    if read == 'False':
                        readtxt = "NEW "
                    else:
                        readtxt = ""
                    sendMessage(readtxt + "From: " + sender + " " + \
                                date + " " + text, message["user"])
                    cursor.execute("UPDATE tellmsg SET read = 'True' " + \
                                   "WHERE receiver = ?", (message["user"],))
            con.commit()
            con.close()
            dbaccess("release")
        except Exception, e:
            if "no such table" in str(e):
                createTellTable(cursor)
                dbaccess("release")
                incomingWhois(message, sendMessage, dbaccess)
            else:
                dbaccess("release")
                raise
    
    
def read(message, sendMessage, dbaccess, response):
    searchmessages = True
    startmess = 0
    if len(string.split(message["text"], " ")) > 1:
        try:
            startmess = int(string.split(message["text"], " ")[1])
        except:
            sendMessage("<Syntax Error>, try !HELP READ", response)
            searchmessages = False
    if searchmessages == True:
        sendMessage("Searching your messages. Note: You must be " + \
                    "identified by NickServ, otherwise you got " + \
                    "no messages.", message["sender"])
        lower_sender = string.lower(message["sender"])
        awaited_users_lock.acquire()
        calltime = time.time()
        awaited_users[lower_sender] = {}
        awaited_users[lower_sender]["time"] = calltime
        awaited_users[lower_sender]["startmess"] = startmess
        awaited_users_lock.release()
        sendMessage("WHOIS " + lower_sender, "", msgtype="SYSTEM")
        time.sleep(20)
        awaited_users_lock.acquire()
        if lower_sender in awaited_users \
           and awaited_users[lower_sender]["time"] == calltime:
            sendMessage("Sorry, I got no identification via WHOIS/NICKSERV. " + \
                        "Possible Problems: you don't use the Nickname you " + \
                        "are registered for, you are not identified via " + \
                        "NickServ or the bot is too busy. Sorry.", \
                        message["sender"])
            del awaited_users[lower_sender]
        awaited_users_lock.release()


def tell(message, sendMessage, dbaccess, response):
    try:
        con = dbaccess()
        cursor = con.cursor()
        sender = message["sender"]
        receiver = string.lower(string.split(message["text"], " ")[1])
        text = message["text"][string.index(message["text"], " ", 6):]
        now = datetime.datetime.now()
        cursor.execute("INSERT INTO tellmsg (sender, receiver, " + \
                       "date, text, read) VALUES (?, ?, ?, ?, ?)", \
                       (sender, receiver, now, text, 'False'))
        sendMessage(message["sender"] + ": your message has been saved.", \
                    response)
        con.commit()
        con.close()
        dbaccess("release")
    except Exception, e:
        if "no such table" in str(e):
            createTellTable(cursor)
            con.commit()
            con.close()
            dbaccess("release")
            tell(message, sendMessage, cursor, response)
        else:
            dbaccess("release")
            raise

def createTellTable(cursor):
    cursor.execute("CREATE TABLE tellmsg (" + \
                   "id INTEGER PRIMARY KEY, " + \
                   "sender VARCHAR, " + \
                   "receiver VARCHAR, " + \
                   "date TIMESTAMP, " + \
                   "text VARCHAR, " + \
                   "read BOOLEAN)")
