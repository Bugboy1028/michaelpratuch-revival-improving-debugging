"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Isidore - Python IRC Bot

Copyright (C) 2010 Sebastian Meyer (s.meyer@drachenjaeger.eu)

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this 
program; if not, see <http://www.gnu.org/licenses/

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import string
import datetime

def start():
    print "Module for logging into a database..."
    return logger

def logInDB(cursor, message):
        cursor.execute("INSERT INTO chatlog " + \
                       "(time, sender, shost, type, receiver, textmes) " + \
                       "VALUES (?, ?, ?, ?, ?, ?)",
                       (message["time"], message["sender"], \
                        message["shost"], message["type"], \
                        message["receiver"], message["text"]))

def logger(message, sendMessage, dbaccess):
    if message["type"] != "WHOISRESP":
        try:
            con = dbaccess()
            cursor = con.cursor()
            try:
                logInDB(cursor, message)
            except Exception, e:
                if "no such table" in str(e):
                    createTable(cursor, message)
                else:
                    raise
            # f = open("logging.txt", "a")
            # f.write(str(message["time"]) + " " + message["sender"] + " " + \
            #         message["shost"] + " " + \
            #         message["type"] + " " + message["receiver"] + " " + \
            #         message["text"] + "\r\n")
            # f.close()
            if string.lower(string.split(message["text"], " ")[0]) == "!help" \
               and len(string.split(message["text"], " ")) == 1:
                sendMessage("!SEEN <Nick> : tells when <Nick> was " + \
                            "seen the last time", message["sender"])
            elif string.lower(message["text"])[0:5] == "!seen":
                lastseen(cursor, message, sendMessage)
            con.commit()
            con.close()
            dbaccess("release")
        except Exception:
            dbaccess("release")
            raise
    

def lastseen(cursor, message, sendMessage):
    if message["receiver"][0] == "#":
        response = message["receiver"]
    else:
        response = message["sender"]
    if len(string.split(message["text"], " ")) is not 2:
        sendMessage("<Syntax Error>, try: !SEEN <Nick>", response)
    else:
        searchfor = string.split(message["text"], " ")[1]
        result = cursor.execute("SELECT " + \
                                "time, sender, shost, " + \
                                "type, receiver, textmes " + \
                                "FROM chatlog " + \
                                "WHERE upper(sender) = ? " + \
                                "ORDER BY time DESC LIMIT 1",
                                (string.upper(searchfor),)).fetchall()
        if len(result) is not 1:
            sendMessage("I never saw " + searchfor, response)
        else:
            tup = result[0]
            print tup
            time = tup[0]
            sender = tup[1]
            shost = tup[2]
            mtype = tup[3]
            receiver = tup[4]
            text = tup[5]
            ago = str(datetime.datetime.now() - time)
            info = "no info for action " + mtype
            if mtype == "JOIN":
                info = "JOIN " + text
            elif mtype == "NICK":
                info = "changed NICK to " + text
            elif mtype == "PART":
                info = "LEAVING " + receiver
            elif mtype == "PRIVMSG":
                info = "wrote a message"
            elif mtype == "QUIT":
                info = "QUIT: " + text
            elif mtype == "TOPIC":
                info = "changed the topic"
            answer = "Last time I saw %s was %s (%s ago): %s " \
                     % (sender, str(time)[:16], \
                        ago[:string.rfind(ago, ".")], info)
            sendMessage(answer, response)
        

def createTable(cursor, message):
    print "LOGDB: Trying to create database..."
    cursor.execute("CREATE TABLE chatlog " + \
                   "(time TIMESTAMP, sender VARCHAR, shost VARCHAR, " + \
                   "type VARCHAR, receiver VARCHAR, textmes VARCHAR)")
    logInDB(cursor, message)
